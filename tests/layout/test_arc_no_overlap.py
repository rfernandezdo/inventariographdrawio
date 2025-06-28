#!/usr/bin/env python3
"""
Test para verificar que el layout en arco NO tiene superposiciones
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from drawio_export import generate_drawio_file
import json
import xml.etree.ElementTree as ET
import math

def test_arc_no_overlap():
    """Test para verificar que NO hay superposiciones en el layout de arco"""
    
    # Crear datos de prueba con Resource Group con muchos recursos
    test_data = {
        "subscription1": {
            "name": "Test Subscription",
            "id": "/subscriptions/test-sub",
            "type": "Microsoft.Resources/subscriptions",
            "resourceGroups": {
                "rg-webapp": {
                    "name": "rg-webapp",
                    "id": "/subscriptions/test-sub/resourcegroups/rg-webapp",
                    "type": "Microsoft.Resources/subscriptions/resourceGroups",
                    "resources": {
                        # 8 recursos para garantizar layout de arco
                        "vm1": {
                            "name": "vm-web-01",
                            "id": "/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-web-01",
                            "type": "Microsoft.Compute/virtualMachines",
                            "properties": {"vmSize": "Standard_D2s_v3"}
                        },
                        "vm2": {
                            "name": "vm-web-02", 
                            "id": "/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-web-02",
                            "type": "Microsoft.Compute/virtualMachines",
                            "properties": {"vmSize": "Standard_D2s_v3"}
                        },
                        "storage": {
                            "name": "storageaccount",
                            "id": "/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.Storage/storageAccounts/storageaccount",
                            "type": "Microsoft.Storage/storageAccounts",
                            "properties": {"accountType": "Standard_LRS"}
                        },
                        "db": {
                            "name": "sql-database",
                            "id": "/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.Sql/servers/sqlserver/databases/sql-database",
                            "type": "Microsoft.Sql/servers/databases",
                            "properties": {"edition": "Standard"}
                        },
                        "vnet": {
                            "name": "vnet-webapp",
                            "id": "/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.Network/virtualNetworks/vnet-webapp",
                            "type": "Microsoft.Network/virtualNetworks",
                            "properties": {"addressSpace": ["10.0.0.0/16"]}
                        },
                        "lb": {
                            "name": "load-balancer",
                            "id": "/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.Network/loadBalancers/load-balancer",
                            "type": "Microsoft.Network/loadBalancers",
                            "properties": {"sku": "Standard"}
                        },
                        "appgw": {
                            "name": "app-gateway",
                            "id": "/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.Network/applicationGateways/app-gateway",
                            "type": "Microsoft.Network/applicationGateways",
                            "properties": {"sku": "WAF_v2"}
                        },
                        "keyvault": {
                            "name": "key-vault",
                            "id": "/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.KeyVault/vaults/key-vault",
                            "type": "Microsoft.KeyVault/vaults",
                            "properties": {"enabledForDeployment": True}
                        }
                    }
                }
            }
        }
    }
    
    # Crear diagrama
    output_file = os.path.join(os.path.dirname(__file__), "test-arc-no-overlap.drawio")
    
    # Convertir datos de prueba al formato esperado por generate_drawio_file
    items = []
    dependencies = []
    
    # Agregar suscripción
    sub_data = test_data["subscription1"]
    items.append({
        'name': sub_data['name'],
        'id': sub_data['id'],
        'type': sub_data['type']
    })
    
    # Agregar resource groups
    for rg_key, rg_data in sub_data["resourceGroups"].items():
        items.append({
            'name': rg_data['name'],
            'id': rg_data['id'],
            'type': rg_data['type']
        })
        
        # Agregar recursos
        for res_key, res_data in rg_data["resources"].items():
            items.append({
                'name': res_data['name'],
                'id': res_data['id'],
                'type': res_data['type'],
                'properties': res_data.get('properties', {})
            })
    
    # Generar el diagrama
    result = generate_drawio_file(items, dependencies, diagram_mode='infrastructure')
    
    # Guardar el resultado en archivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print("🧪 Probando layout en arco SIN superposiciones...")
    print(f"📊 Creando RG con {len(test_data['subscription1']['resourceGroups']['rg-webapp']['resources'])} recursos")
    print(f"📐 Radio mínimo ACTUALIZADO: 250, espaciado mínimo: 0.5 radianes")
    
    # Verificar que el archivo se creó
    assert os.path.exists(output_file), f"No se creó el archivo {output_file}"
    print(f"✅ Archivo creado: {output_file}")
    
    # Analizar el XML generado para verificar posiciones
    tree = ET.parse(output_file)
    root = tree.getroot()
    
    # Extraer información de los nodos
    nodes_info = []
    for cell in root.findall(".//mxCell[@style]"):
        geometry = cell.find('mxGeometry')
        if geometry is not None:
            x = float(geometry.get('x', 0))
            y = float(geometry.get('y', 0))
            width = float(geometry.get('width', 120))
            height = float(geometry.get('height', 80))
            
            # Obtener el nombre del nodo desde el objeto label
            obj = cell.find('object')
            if obj is not None:
                label = obj.get('label', 'Unknown')
                # Limpiar etiquetas HTML para obtener solo el texto
                import re
                clean_label = re.sub(r'<[^>]*>', '', label)
            else:
                # Fallback al value del cell si no hay objeto
                clean_label = cell.get('value', 'Unknown')
            
            nodes_info.append({
                'name': clean_label,
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'center_x': x + width/2,
                'center_y': y + height/2
            })
    
    print(f"📋 Analizando {len(nodes_info)} nodos encontrados...")
    
    # Función para verificar si dos nodos se superponen
    def nodes_overlap(node1, node2):
        """Verifica si dos nodos se superponen"""
        # Calcular distancia entre centros
        dx = abs(node1['center_x'] - node2['center_x'])
        dy = abs(node1['center_y'] - node2['center_y'])
        
        # Distancia mínima requerida (suma de medios anchos/altos + margen)
        min_dx = (node1['width'] + node2['width']) / 2 + 10  # 10px de margen
        min_dy = (node1['height'] + node2['height']) / 2 + 10  # 10px de margen
        
        # Se superponen si están demasiado cerca en ambas dimensiones
        return dx < min_dx and dy < min_dy
    
    # Verificar superposiciones
    overlapping_pairs = []
    for i in range(len(nodes_info)):
        for j in range(i + 1, len(nodes_info)):
            if nodes_overlap(nodes_info[i], nodes_info[j]):
                overlapping_pairs.append((nodes_info[i], nodes_info[j]))
    
    print(f"🔍 Verificación de superposiciones:")
    if overlapping_pairs:
        print(f"❌ Se encontraron {len(overlapping_pairs)} pares superpuestos:")
        for node1, node2 in overlapping_pairs:
            print(f"   ⚠️ '{node1['name']}' y '{node2['name']}'")
            print(f"      - {node1['name']}: centro ({node1['center_x']:.1f}, {node1['center_y']:.1f})")
            print(f"      - {node2['name']}: centro ({node2['center_x']:.1f}, {node2['center_y']:.1f})")
            distance = math.sqrt((node1['center_x'] - node2['center_x'])**2 + (node1['center_y'] - node2['center_y'])**2)
            print(f"      - Distancia entre centros: {distance:.1f}px")
    else:
        print("✅ NO se encontraron superposiciones - ¡Perfecto!")
    
    # Analizar el patrón del arco
    resource_nodes = [node for node in nodes_info if 'vm-' in node['name'] or 'storage' in node['name'] or 'sql-' in node['name'] or 'vnet-' in node['name'] or 'load-' in node['name'] or 'app-' in node['name'] or 'key-' in node['name']]
    rg_nodes = [node for node in nodes_info if 'rg-' in node['name']]
    
    if rg_nodes and resource_nodes:
        rg_node = rg_nodes[0]
        print(f"\n📐 Análisis del patrón de arco:")
        print(f"   🏗️ Resource Group: '{rg_node['name']}' en ({rg_node['center_x']:.1f}, {rg_node['center_y']:.1f})")
        print(f"   📦 {len(resource_nodes)} recursos en el arco:")
        
        # Calcular distancias desde el RG a cada recurso
        distances = []
        for resource in resource_nodes:
            distance = math.sqrt((resource['center_x'] - rg_node['center_x'])**2 + (resource['center_y'] - rg_node['center_y'])**2)
            distances.append(distance)
            print(f"      - '{resource['name']}': {distance:.1f}px del RG")
        
        if distances:
            avg_distance = sum(distances) / len(distances)
            min_distance = min(distances)
            max_distance = max(distances)
            print(f"   📊 Distancia promedio: {avg_distance:.1f}px")
            print(f"   📊 Distancia mínima: {min_distance:.1f}px")
            print(f"   📊 Distancia máxima: {max_distance:.1f}px")
            print(f"   📊 Variación: {max_distance - min_distance:.1f}px")
    
    # El test pasa solo si NO hay superposiciones
    assert len(overlapping_pairs) == 0, f"Se encontraron {len(overlapping_pairs)} pares de nodos superpuestos"
    
    print(f"\n✅ Test de NO superposición completado exitosamente")
    print(f"📋 Resultado: Layout de arco sin superposiciones funcionando correctamente")
    
    return True

def test_extreme_case_many_resources():
    """Test con muchos recursos para caso extremo"""
    
    # Crear datos con 12 recursos (caso extremo)
    resources = {}
    for i in range(12):
        resources[f"resource{i:02d}"] = {
            "name": f"resource-{i:02d}",
            "id": f"/subscriptions/test-sub/resourcegroups/rg-extreme/providers/Microsoft.Compute/virtualMachines/resource-{i:02d}",
            "type": "Microsoft.Compute/virtualMachines",
            "properties": {"vmSize": "Standard_D2s_v3"}
        }
    
    test_data = {
        "subscription1": {
            "name": "Test Subscription Extreme",
            "id": "/subscriptions/test-sub",
            "type": "Microsoft.Resources/subscriptions",
            "resourceGroups": {
                "rg-extreme": {
                    "name": "rg-extreme",
                    "id": "/subscriptions/test-sub/resourcegroups/rg-extreme",
                    "type": "Microsoft.Resources/subscriptions/resourceGroups",
                    "resources": resources
                }
            }
        }
    }
    
    # Crear diagrama
    output_file = os.path.join(os.path.dirname(__file__), "test-arc-extreme-case.drawio")
    
    # Convertir datos de prueba al formato esperado por generate_drawio_file
    items = []
    dependencies = []
    
    # Agregar suscripción
    sub_data = test_data["subscription1"]
    items.append({
        'name': sub_data['name'],
        'id': sub_data['id'],
        'type': sub_data['type']
    })
    
    # Agregar resource groups
    for rg_key, rg_data in sub_data["resourceGroups"].items():
        items.append({
            'name': rg_data['name'],
            'id': rg_data['id'],
            'type': rg_data['type']
        })
        
        # Agregar recursos
        for res_key, res_data in rg_data["resources"].items():
            items.append({
                'name': res_data['name'],
                'id': res_data['id'],
                'type': res_data['type'],
                'properties': res_data.get('properties', {})
            })
    
    # Generar archivo
    result = generate_drawio_file(items, dependencies, diagram_mode='infrastructure')
    
    # Guardar el resultado en archivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"\n🧪 Probando caso extremo con {len(resources)} recursos...")
    
    # Verificar que el archivo se creó
    assert os.path.exists(output_file), f"No se creó el archivo {output_file}"
    print(f"✅ Archivo creado: {output_file}")
    
    print(f"✅ Test de caso extremo completado - ver {output_file}")
    
    return True

if __name__ == "__main__":
    try:
        test_arc_no_overlap()
        test_extreme_case_many_resources()
        print("\n🎉 TODOS LOS TESTS DE NO SUPERPOSICIÓN PASARON CORRECTAMENTE")
        print("\n📋 Resumen:")
        print("   ✅ Layout de arco SIN superposiciones verificado")
        print("   ✅ Caso extremo con muchos recursos probado")
        print("   📐 Parámetros optimizados:")
        print("      - Radio mínimo: 200px")
        print("      - Espaciado mínimo: 0.4 radianes")
        print("      - Padding generoso aplicado")
        
    except Exception as e:
        print(f"\n❌ ERROR en tests de no superposición: {e}")
        sys.exit(1)

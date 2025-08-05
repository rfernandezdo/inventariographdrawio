#!/usr/bin/env python3
"""
Generador directo usando el layout de red con NSGs y Route Tables multi-subnet
"""

import sys
import os
import json

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from drawio.layouts.network import generate_network_layout
from drawio.single_page import generate_drawio_file

def load_demo_data():
    """Carga los datos de demostración"""
    data_file = "data/demo_nsg_rt_multi_subnet.json"
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data['items'], data['dependencies']

def generate_network_demo():
    """Genera un diagrama de red usando directamente el layout mejorado"""
    
    print("🎯 Cargando datos de demostración...")
    items, dependencies = load_demo_data()
    
    print(f"📊 Datos cargados: {len(items)} recursos, {len(dependencies)} dependencias")
    
    # Mostrar estadísticas de NSGs y Route Tables multi-subnet
    nsgs_multi_subnet = []
    route_tables_multi_subnet = []
    
    for item in items:
        item_type = item.get('type', 'unknown')
        
        # Verificar NSGs con múltiples subnets
        if item_type == 'Microsoft.Network/networkSecurityGroups':
            subnets = item.get('properties', {}).get('subnets', [])
            if len(subnets) > 1:
                nsgs_multi_subnet.append({
                    'name': item['name'],
                    'subnet_count': len(subnets),
                    'subnets': [s['id'].split('/')[-1] for s in subnets]
                })
        
        # Verificar Route Tables con múltiples subnets
        elif item_type == 'Microsoft.Network/routeTables':
            subnets = item.get('properties', {}).get('subnets', [])
            if len(subnets) > 1:
                route_tables_multi_subnet.append({
                    'name': item['name'],
                    'subnet_count': len(subnets),
                    'subnets': [s['id'].split('/')[-1] for s in subnets]
                })
    
    print(f"\n🔒 NSGs con múltiples subnets: {len(nsgs_multi_subnet)}")
    for nsg in nsgs_multi_subnet:
        print(f"  • {nsg['name']}: {nsg['subnet_count']} subnets")
        print(f"    → {', '.join(nsg['subnets'])}")
    
    print(f"\n🛣️ Route Tables con múltiples subnets: {len(route_tables_multi_subnet)}")
    for rt in route_tables_multi_subnet:
        print(f"  • {rt['name']}: {rt['subnet_count']} subnets")
        print(f"    → {', '.join(rt['subnets'])}")
    
    print(f"\n🚀 Generando layout de red...")
    
    try:
        # Usar directamente el layout de red
        extended_items, node_positions, group_info, resource_to_parent_id = generate_network_layout(
            items, dependencies
        )
        
        print(f"✅ Layout generado exitosamente!")
        print(f"  📊 Elementos originales: {len(items)}")
        print(f"  📊 Elementos extendidos: {len(extended_items)}")
        print(f"  📍 Posiciones: {len(node_positions)}")
        print(f"  📦 Grupos/Contenedores: {len(group_info)}")
        
        # Analizar elementos virtuales creados
        virtual_elements = []
        nsg_instances = {}
        rt_instances = {}
        
        for i, item in enumerate(extended_items):
            item_type = item.get('type', '').lower()
            virtual_subnet = item.get('_virtual_subnet_id')
            
            if virtual_subnet:
                virtual_elements.append({
                    'index': i,
                    'name': item.get('name'),
                    'type': item_type,
                    'virtual_subnet': virtual_subnet.split('/')[-1],
                    'position': node_positions.get(i),
                    'parent': resource_to_parent_id.get(i)
                })
            
            # Contar instancias de NSGs
            if 'networksecuritygroups' in item_type:
                name = item.get('name')
                nsg_instances[name] = nsg_instances.get(name, 0) + 1
            
            # Contar instancias de Route Tables
            elif 'routetables' in item_type:
                name = item.get('name')
                rt_instances[name] = rt_instances.get(name, 0) + 1
        
        print(f"\n🔄 Elementos virtuales creados: {len(virtual_elements)}")
        for elem in virtual_elements:
            print(f"  • {elem['name']} (#{elem['index']}) → subnet: {elem['virtual_subnet']}")
            print(f"    Posición: {elem['position']}, Padre: {elem['parent']}")
        
        print(f"\n📊 Instancias totales por elemento:")
        print("  NSGs:")
        for name, count in nsg_instances.items():
            print(f"    • {name}: {count} instancias")
        
        print("  Route Tables:")
        for name, count in rt_instances.items():
            print(f"    • {name}: {count} instancias")
        
        # Generar el XML del diagrama
        print(f"\n🎨 Generando diagrama XML...")
        xml_content = generate_drawio_file(
            extended_items, dependencies, 
            embed_data=True, 
            diagram_mode='network',
            no_hierarchy_edges=False
        )
        
        # Guardar archivo
        output_file = "demo_network_multi_subnet.drawio"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"✅ Diagrama guardado: {output_file}")
        
        # Verificar contenido del diagrama
        nsg_count_in_xml = sum(xml_content.count(name) for name in nsg_instances.keys())
        rt_count_in_xml = sum(xml_content.count(name) for name in rt_instances.keys())
        
        print(f"\n🔍 Verificación del XML generado:")
        print(f"  • NSGs mencionados: {nsg_count_in_xml} veces")
        print(f"  • Route Tables mencionados: {rt_count_in_xml} veces")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🌐 Generador de Diagrama de Red - NSGs y Route Tables Multi-Subnet")
    print("=" * 65)
    
    success = generate_network_demo()
    
    if success:
        print("\n🎉 ¡Generación exitosa!")
        print("\n📁 Archivo generado:")
        print("  • demo_network_multi_subnet.drawio")
        print("\n💡 Instrucciones:")
        print("  1. Abre el archivo en https://app.diagrams.net")
        print("  2. Verás NSGs y Route Tables duplicados en sus respectivas subnets")
        print("  3. Ejemplo: 'demo-nsg-web-tier' aparecerá en 3 subnets diferentes")
        print("  4. Cada instancia está posicionada dentro de su subnet correspondiente")
        
        return 0
    else:
        print("\n❌ Error en la generación")
        return 1

if __name__ == "__main__":
    sys.exit(main())

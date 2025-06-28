#!/usr/bin/env python3
"""
Test del arco HACIA ABAJO - RG arriba, recursos abajo en arco
"""

import sys
import os
sys.path.append('src')

from drawio_export import generate_drawio_file
import xml.etree.ElementTree as ET
import math
import re

def test_arc_down():
    """Test del arco hacia abajo"""
    
    print("🧪 Probando arco hacia ABAJO (RG arriba, recursos abajo)...")
    
    # Test con 6 recursos para un buen arco
    items = [
        {'name': 'Test Sub', 'id': '/subscriptions/test', 'type': 'Microsoft.Resources/subscriptions'},
        {'name': 'rg-webapp', 'id': '/subscriptions/test/resourcegroups/rg-webapp', 'type': 'Microsoft.Resources/subscriptions/resourceGroups'},
        {'name': 'vm-web-01', 'id': '/subscriptions/test/resourcegroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-web-01', 'type': 'Microsoft.Compute/virtualMachines'},
        {'name': 'vm-web-02', 'id': '/subscriptions/test/resourcegroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-web-02', 'type': 'Microsoft.Compute/virtualMachines'},
        {'name': 'storage', 'id': '/subscriptions/test/resourcegroups/rg-webapp/providers/Microsoft.Storage/storageAccounts/storage', 'type': 'Microsoft.Storage/storageAccounts'},
        {'name': 'database', 'id': '/subscriptions/test/resourcegroups/rg-webapp/providers/Microsoft.Sql/servers/srv/databases/db', 'type': 'Microsoft.Sql/servers/databases'},
        {'name': 'vnet', 'id': '/subscriptions/test/resourcegroups/rg-webapp/providers/Microsoft.Network/virtualNetworks/vnet', 'type': 'Microsoft.Network/virtualNetworks'},
        {'name': 'vault', 'id': '/subscriptions/test/resourcegroups/rg-webapp/providers/Microsoft.KeyVault/vaults/vault', 'type': 'Microsoft.KeyVault/vaults'}
    ]
    
    dependencies = []
    
    print(f"📦 Recursos: {len([i for i in items if '/providers/' in i['id']])}")
    print("   Debería crear arco hacia abajo con RG en la parte superior")
    
    # Generar diagrama
    result = generate_drawio_file(items, dependencies, diagram_mode='infrastructure')
    
    # Guardar
    output_file = 'test-arc-down.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"✅ Generado: {output_file}")
    
    # Analizar posiciones
    tree = ET.parse(output_file)
    root = tree.getroot()
    
    nodes = []
    for cell in root.findall(".//mxCell[@style]"):
        geometry = cell.find('mxGeometry')
        if geometry is not None:
            x = float(geometry.get('x', 0))
            y = float(geometry.get('y', 0))
            w = float(geometry.get('width', 80))
            h = float(geometry.get('height', 80))
            
            obj = cell.find('object')
            if obj is not None:
                label = obj.get('label', 'Unknown')
                clean_name = re.sub(r'<[^>]*>', '', label)
            else:
                clean_name = cell.get('value', 'Unknown')
            
            nodes.append({
                'name': clean_name,
                'x': x, 'y': y, 'w': w, 'h': h,
                'cx': x + w/2, 'cy': y + h/2
            })
    
    print(f"\n📋 Posiciones (verificando arco hacia abajo):")
    
    # Encontrar RG y recursos
    rg_node = None
    resource_nodes = []
    
    for node in nodes:
        if 'rg-' in node['name']:
            rg_node = node
            print(f"   🏗️ {node['name']:15}: centro=({node['cx']:7.1f}, {node['cy']:7.1f}) [RG]")
        elif any(x in node['name'] for x in ['vm-', 'storage', 'database', 'vnet', 'vault']):
            resource_nodes.append(node)
            print(f"   📦 {node['name']:15}: centro=({node['cx']:7.1f}, {node['cy']:7.1f})")
        else:
            print(f"   📋 {node['name']:15}: centro=({node['cx']:7.1f}, {node['cy']:7.1f})")
    
    # Verificar que el arco está hacia abajo
    if rg_node and resource_nodes:
        print(f"\n📐 Análisis del arco:")
        print(f"   🏗️ RG en: ({rg_node['cx']:.1f}, {rg_node['cy']:.1f})")
        
        resources_below = 0
        resources_above = 0
        
        for res in resource_nodes:
            if res['cy'] > rg_node['cy']:
                resources_below += 1
                direction = "ABAJO ✅"
            else:
                resources_above += 1
                direction = "ARRIBA ❌"
            
            distance = math.sqrt((res['cx'] - rg_node['cx'])**2 + (res['cy'] - rg_node['cy'])**2)
            print(f"   📦 {res['name']:12}: {distance:6.1f}px, {direction}")
        
        print(f"\n📊 Resumen del arco:")
        print(f"   ✅ Recursos abajo del RG: {resources_below}")
        print(f"   ❌ Recursos arriba del RG: {resources_above}")
        
        if resources_below > resources_above:
            print("   🎉 ¡ARCO HACIA ABAJO CORRECTO!")
            return True
        else:
            print("   ⚠️ El arco no está completamente hacia abajo")
            return False
    
    return False

if __name__ == "__main__":
    try:
        success = test_arc_down()
        if success:
            print("\n🎉 ARCO HACIA ABAJO IMPLEMENTADO CORRECTAMENTE!")
            print("   ✅ RG en la parte superior")
            print("   ✅ Recursos formando arco hacia abajo")
        else:
            print("\n❌ El arco necesita ajustes")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Test para verificar que las aristas de recursos bajo RG son rectas
"""

import sys
import os
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from drawio_export import generate_drawio_file
import xml.etree.ElementTree as ET

def test_straight_edges():
    """Test para verificar aristas rectas en layout de arco"""
    
    print("🧪 Verificando aristas rectas para recursos bajo Resource Group...")
    
    # Crear datos de prueba con RG y recursos
    items = [
        {'name': 'Test Sub', 'id': '/subscriptions/test', 'type': 'Microsoft.Resources/subscriptions'},
        {'name': 'rg-test', 'id': '/subscriptions/test/resourcegroups/rg-test', 'type': 'Microsoft.Resources/subscriptions/resourceGroups'},
        {'name': 'vm1', 'id': '/subscriptions/test/resourcegroups/rg-test/providers/Microsoft.Compute/virtualMachines/vm1', 'type': 'Microsoft.Compute/virtualMachines'},
        {'name': 'vm2', 'id': '/subscriptions/test/resourcegroups/rg-test/providers/Microsoft.Compute/virtualMachines/vm2', 'type': 'Microsoft.Compute/virtualMachines'},
        {'name': 'storage', 'id': '/subscriptions/test/resourcegroups/rg-test/providers/Microsoft.Storage/storageAccounts/storage', 'type': 'Microsoft.Storage/storageAccounts'},
        {'name': 'database', 'id': '/subscriptions/test/resourcegroups/rg-test/providers/Microsoft.Sql/servers/srv/databases/db', 'type': 'Microsoft.Sql/servers/databases'}
    ]
    
    dependencies = []
    
    print(f"📦 Generando diagrama con {len([i for i in items if '/providers/' in i['id']])} recursos...")
    
    # Generar diagrama
    result = generate_drawio_file(items, dependencies, diagram_mode='infrastructure')
    
    # Guardar para inspección
    output_file = 'test-straight-edges.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"✅ Generado: {output_file}")
    
    # Parsear XML y analizar estilos de aristas
    tree = ET.parse(output_file)
    root = tree.getroot()
    
    straight_edges = 0
    orthogonal_edges = 0
    other_edges = 0
    
    print(f"\n📋 Analizando estilos de aristas:")
    
    for edge in root.findall(".//mxCell[@edge='1']"):
        style = edge.get('style', '')
        edge_id = edge.get('id', 'unknown')
        
        if 'edgeStyle=straight' in style:
            straight_edges += 1
            print(f"   📏 {edge_id}: RECTA ✅")
        elif 'edgeStyle=orthogonalEdgeStyle' in style:
            orthogonal_edges += 1
            print(f"   📐 {edge_id}: ORTOGONAL")
        else:
            other_edges += 1
            print(f"   ❓ {edge_id}: OTRO ({style[:50]}...)")
    
    print(f"\n📊 Resumen de estilos:")
    print(f"   📏 Aristas rectas: {straight_edges}")
    print(f"   📐 Aristas ortogonales: {orthogonal_edges}")
    print(f"   ❓ Otros estilos: {other_edges}")
    
    # Verificar que hay aristas rectas (para el layout de arco)
    if straight_edges > 0:
        print(f"\n✅ ¡PERFECTO! Se encontraron {straight_edges} aristas rectas")
        print("   Las conexiones de recursos al RG usan líneas rectas")
        return True
    else:
        print(f"\n⚠️ No se encontraron aristas rectas")
        print("   Puede que el layout de arco no se haya activado")
        return False

if __name__ == "__main__":
    try:
        success = test_straight_edges()
        if success:
            print("\n🎉 ¡Las aristas rectas están funcionando correctamente!")
        else:
            print("\n❌ Las aristas no son rectas como se esperaba")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

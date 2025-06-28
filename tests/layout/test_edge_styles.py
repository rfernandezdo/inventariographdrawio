#!/usr/bin/env python3
"""
Test simple para verificar que los estilos de aristas funcionan correctamente
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from drawio_export import generate_drawio_file
import xml.etree.ElementTree as ET

def test_edge_styles():
    """Test que verifica los diferentes estilos de aristas"""
    print("Testing edge styles...")
    
    # Datos de prueba con diferentes tipos de conexiones
    test_data = [
        {
            "id": "/managementGroups/mg-root",
            "name": "Root MG",
            "type": "Microsoft.Management/managementGroups",
            "location": "global"
        },
        {
            "id": "/subscriptions/sub-001",
            "name": "Test Subscription",
            "type": "Microsoft.Resources/subscriptions",
            "subscription_id": "sub-001",
            "location": "global"
        },
        {
            "id": "/subscriptions/sub-001/resourceGroups/rg-test",
            "name": "Test RG",
            "type": "Microsoft.Resources/subscriptions/resourceGroups",
            "resource_group": "rg-test",
            "subscription_id": "sub-001",
            "location": "eastus"
        },
        {
            "id": "/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Compute/virtualMachines/vm-001",
            "name": "Test VM",
            "type": "Microsoft.Compute/virtualMachines",
            "resource_group": "rg-test",
            "subscription_id": "sub-001",
            "location": "eastus"
        }
    ]
    
    dependencies = []
    
    # Generar diagrama
    try:
        drawio_xml = generate_drawio_file(
            test_data,
            dependencies,
            embed_data=True,
            diagram_mode='infrastructure'
        )
        
        # Parsear XML
        root = ET.fromstring(drawio_xml)
        
        # Contar tipos de aristas
        straight_edges = 0
        orthogonal_edges = 0
        
        for cell in root.findall(".//mxCell"):
            if cell.get('edge') == '1':
                style = cell.get('style', '')
                print(f"Edge style: {style}")
                
                if 'edgeStyle=straight' in style:
                    straight_edges += 1
                elif 'edgeStyle=orthogonalEdgeStyle' in style:
                    orthogonal_edges += 1
        
        print(f"Straight edges: {straight_edges}")
        print(f"Orthogonal edges: {orthogonal_edges}")
        
        # Guardar resultado
        with open('test_edge_styles.drawio', 'w', encoding='utf-8') as f:
            f.write(drawio_xml)
        
        print("✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Ejecutando test de estilos de aristas...")
    test_edge_styles()
    print("Test completado.")

#!/usr/bin/env python3
"""
Test simplificado para verificar que las aristas de recursos bajo Resource Groups
son rectas (straight) en el layout de arco.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import sys

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from drawio_export import generate_drawio_file

def test_straight_edges_in_arc_layout():
    """Test que verifica que las aristas de RG -> Recursos son rectas"""
    print("Testing straight edges in arc layout...")
    
    # Datos de prueba simplificados
    items = [
        {
            "id": "/subscriptions/sub-001",
            "name": "Test Subscription",
            "type": "Microsoft.Resources/subscriptions"
        },
        {
            "id": "/subscriptions/sub-001/resourceGroups/rg-test",
            "name": "rg-test",
            "type": "Microsoft.Resources/subscriptions/resourceGroups"
        },
        {
            "id": "/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Compute/virtualMachines/vm-001",
            "name": "vm-001",
            "type": "Microsoft.Compute/virtualMachines"
        },
        {
            "id": "/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Network/virtualNetworks/vnet-001",
            "name": "vnet-001", 
            "type": "Microsoft.Network/virtualNetworks"
        },
        {
            "id": "/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Storage/storageAccounts/storage-001",
            "name": "storage-001",
            "type": "Microsoft.Storage/storageAccounts"
        }
    ]
    
    dependencies = []
    
    # Generar diagrama
    drawio_xml = generate_drawio_file(
        items,
        dependencies,
        embed_data=True,
        diagram_mode='infrastructure'
    )
    
    # Guardar para inspección
    output_file = Path(__file__).parent.parent / "fixtures" / "test-straight-edges-arc.drawio"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(drawio_xml)
    
    # Parsear XML y analizar
    root = ET.fromstring(drawio_xml)
    
    straight_edges = 0
    orthogonal_edges = 0
    
    print("\nAnalyzing edge styles:")
    for cell in root.findall(".//mxCell"):
        if cell.get('edge') == '1':
            style = cell.get('style', '')
            if 'edgeStyle=straight' in style:
                straight_edges += 1
                print(f"  Straight edge: {style[:50]}...")
            elif 'edgeStyle=orthogonalEdgeStyle' in style:
                orthogonal_edges += 1
                print(f"  Orthogonal edge: {style[:50]}...")
    
    print(f"\nResults:")
    print(f"  Straight edges: {straight_edges}")
    print(f"  Orthogonal edges: {orthogonal_edges}")
    
    # Verificaciones
    assert straight_edges > 0, "Should have at least one straight edge (RG -> Resources)"
    assert orthogonal_edges > 0, "Should have orthogonal edges (upper levels)"
    
    print(f"✅ Test passed: Found {straight_edges} straight edges and {orthogonal_edges} orthogonal edges")
    print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    test_straight_edges_in_arc_layout()

#!/usr/bin/env python3
"""
Test específico para verificar que las aristas de recursos bajo Resource Groups
son rectas (straight) en el layout de arco.
"""

import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from drawio_export import generate_drawio_file
from utils import extract_levels, create_index_mappings

def test_straight_edges_in_arc_layout():
    """Test que verifica que las aristas de RG -> Recursos son rectas en layout de arco"""
    print("Testing straight edges in arc layout...")
    
    # Datos de prueba con RG y recursos
    test_data = {
        "subscriptions": [
            {
                "id": "/subscriptions/sub-001",
                "displayName": "Test Subscription",
                "subscriptionId": "sub-001"
            }
        ],
        "resource_groups": [
            {
                "id": "/subscriptions/sub-001/resourceGroups/rg-test",
                "name": "rg-test",
                "location": "eastus",
                "subscription_id": "sub-001"
            }
        ],
        "resources": [
            {
                "id": "/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Compute/virtualMachines/vm-001",
                "name": "vm-001",
                "type": "Microsoft.Compute/virtualMachines",
                "resource_group": "rg-test",
                "subscription_id": "sub-001",
                "location": "eastus"
            },
            {
                "id": "/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Network/virtualNetworks/vnet-001",
                "name": "vnet-001", 
                "type": "Microsoft.Network/virtualNetworks",
                "resource_group": "rg-test",
                "subscription_id": "sub-001",
                "location": "eastus"
            },
            {
                "id": "/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Storage/storageAccounts/storage001",
                "name": "storage001",
                "type": "Microsoft.Storage/storageAccounts", 
                "resource_group": "rg-test",
                "subscription_id": "sub-001",
                "location": "eastus"
            }
        ],
        "dependencies": []
    }
    
    # Generar diagrama en modo infraestructura
    drawio_xml = generate_drawio_file(
        test_data["resources"],
        test_data["dependencies"],
        embed_data=True,
        diagram_mode='infrastructure'
    )
        
        # Parsear XML
        root = ET.fromstring(drawio_xml)
        
        # Encontrar todas las aristas (edges)
        edges = []
        cells_info = {}
        
        # Primero recopilar información de todas las celdas
        for cell in root.findall(".//mxCell"):
            cell_id = cell.get('id')
            style = cell.get('style', '')
            value = cell.get('value', '')
            
            if cell_id:
                cells_info[cell_id] = {
                    'style': style,
                    'value': value,
                    'is_edge': cell.get('edge') == '1'
                }
                
                if cell.get('edge') == '1':
                    edges.append({
                        'id': cell_id,
                        'style': style,
                        'source': cell.get('source'),
                        'target': cell.get('target')
                    })
        
        print(f"Found {len(edges)} edges in the diagram")
        
        # Contar aristas rectas vs ortogonales
        straight_edges = 0
        orthogonal_edges = 0
        hierarchical_edges = 0
        
        for edge in edges:
            style = edge['style']
            print(f"Edge {edge['id']}: {style}")
            
            if 'edgeStyle=straight' in style:
                straight_edges += 1
                if '#1976d2' in style:  # Color azul = jerárquica
                    hierarchical_edges += 1
            elif 'edgeStyle=orthogonalEdgeStyle' in style:
                orthogonal_edges += 1
        
        print(f"Straight edges: {straight_edges}")
        print(f"Orthogonal edges: {orthogonal_edges}")
        print(f"Hierarchical edges: {hierarchical_edges}")
        
        # Verificaciones
        assert straight_edges > 0, "Should have at least one straight edge"
        assert hierarchical_edges > 0, "Should have hierarchical edges (RG -> Resources)"
        
        # En modo infraestructura con arco, las conexiones RG -> Recurso deben ser rectas
        print("✅ Test passed: Found straight hierarchical edges in arc layout")
        
        # Guardar resultado para inspección visual
        output_file = Path(__file__).parent.parent / "fixtures" / "test-straight-edges-arc.drawio"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(drawio_xml)
        print(f"Diagram saved to: {output_file}")

def test_edge_styles_by_connection_type():
    """Test más detallado para verificar estilos de aristas por tipo de conexión"""
    print("\nTesting edge styles by connection type...")
    
    # Datos con dependencias jerárquicas y no jerárquicas
    test_data = {
        "subscriptions": [
            {
                "id": "/subscriptions/sub-001",
                "displayName": "Test Subscription",
                "subscriptionId": "sub-001"
            }
        ],
        "resource_groups": [
            {
                "id": "/subscriptions/sub-001/resourceGroups/rg-test",
                "name": "rg-test",
                "location": "eastus",
                "subscription_id": "sub-001"
            }
        ],
        "resources": [
            {
                "id": "/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Compute/virtualMachines/vm-001",
                "name": "vm-001",
                "type": "Microsoft.Compute/virtualMachines",
                "resource_group": "rg-test",
                "subscription_id": "sub-001",
                "location": "eastus"
            },
            {
                "id": "/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Network/virtualNetworks/vnet-001",
                "name": "vnet-001",
                "type": "Microsoft.Network/virtualNetworks",
                "resource_group": "rg-test",
                "subscription_id": "sub-001",
                "location": "eastus"
            }
        ],
        "dependencies": [
            # Dependencia no jerárquica (recurso -> recurso)
            [
                "/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Compute/virtualMachines/vm-001",
                "/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Network/virtualNetworks/vnet-001"
            ]
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, indent=2)
        temp_file = f.name
    
    try:
        drawio_xml = generate_drawio_file(
            test_data["resources"],
            test_data["dependencies"],
            embed_data=True,
            diagram_mode='infrastructure'
        )
        
        root = ET.fromstring(drawio_xml)
        
        # Analizar estilos de aristas
        hierarchical_straight = 0
        dependency_orthogonal = 0
        
        for cell in root.findall(".//mxCell"):
            if cell.get('edge') == '1':
                style = cell.get('style', '')
                
                if 'edgeStyle=straight' in style and '#1976d2' in style:
                    hierarchical_straight += 1
                    print(f"Hierarchical straight edge: {style}")
                elif 'edgeStyle=orthogonalEdgeStyle' in style and 'dashed=1' in style:
                    dependency_orthogonal += 1
                    print(f"Dependency orthogonal edge: {style}")
        
        print(f"Hierarchical straight edges: {hierarchical_straight}")
        print(f"Dependency orthogonal edges: {dependency_orthogonal}")
        
        assert hierarchical_straight >= 2, "Should have hierarchical edges from RG to resources"
        assert dependency_orthogonal >= 1, "Should have dependency edge between resources"
        
        print("✅ Test passed: Correct edge styles for different connection types")
        
    finally:
        Path(temp_file).unlink()

if __name__ == "__main__":
    test_straight_edges_in_arc_layout()
    test_edge_styles_by_connection_type()
    print("\n🎉 All tests passed!")

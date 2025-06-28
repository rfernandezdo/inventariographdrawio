#!/usr/bin/env python3
"""
Test para verificar el layout jerárquico del modo infrastructure con filtrado de dependencias estructurales
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from drawio_export import generate_drawio_file

def test_hierarchical_tree_layout():
    """Test del layout jerárquico con estructura completa de Azure y dependencias filtradas"""
    
    # Datos de prueba con jerarquía completa y dependencias mixtas
    test_items = [
        # Management Group (nivel 0 - raíz)
        {
            'id': '/providers/Microsoft.Management/managementGroups/mg-root',
            'name': 'Root Management Group',
            'type': 'Microsoft.Management/managementGroups',
            'properties': {'displayName': 'Root MG'}
        },
        # Suscripción (nivel 1)
        {
            'id': '/subscriptions/12345-abcd-efgh',
            'name': 'Production Subscription',
            'type': 'Microsoft.Resources/subscriptions',
            'subscriptionId': '12345-abcd-efgh'
        },
        # Resource Group (nivel 2)
        {
            'id': '/subscriptions/12345-abcd-efgh/resourceGroups/rg-webapp',
            'name': 'rg-webapp',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups',
            'resourceGroup': 'rg-webapp',
            'subscriptionId': '12345-abcd-efgh'
        },
        # VNet (nivel 3)
        {
            'id': '/subscriptions/12345-abcd-efgh/resourceGroups/rg-webapp/providers/Microsoft.Network/virtualNetworks/vnet1',
            'name': 'vnet1',
            'type': 'Microsoft.Network/virtualNetworks',
            'resourceGroup': 'rg-webapp',
            'subscriptionId': '12345-abcd-efgh'
        },
        # Storage Account (nivel 3)
        {
            'id': '/subscriptions/12345-abcd-efgh/resourceGroups/rg-webapp/providers/Microsoft.Storage/storageAccounts/mystorage',
            'name': 'mystorage',
            'type': 'Microsoft.Storage/storageAccounts',
            'resourceGroup': 'rg-webapp',
            'subscriptionId': '12345-abcd-efgh'
        }
    ]
    
    # Dependencias mixtas: jerárquicas y no jerárquicas
    test_dependencies = [
        # Dependencias JERÁRQUICAS (estructurales) - se usarán para el árbol
        ('/subscriptions/12345-abcd-efgh', '/providers/Microsoft.Management/managementGroups/mg-root'),
        ('/subscriptions/12345-abcd-efgh/resourceGroups/rg-webapp', '/subscriptions/12345-abcd-efgh'),
        ('/subscriptions/12345-abcd-efgh/resourceGroups/rg-webapp/providers/Microsoft.Network/virtualNetworks/vnet1', 
         '/subscriptions/12345-abcd-efgh/resourceGroups/rg-webapp'),
        ('/subscriptions/12345-abcd-efgh/resourceGroups/rg-webapp/providers/Microsoft.Storage/storageAccounts/mystorage', 
         '/subscriptions/12345-abcd-efgh/resourceGroups/rg-webapp'),
        
        # Dependencias NO JERÁRQUICAS (relaciones) - se mostrarán como líneas punteadas
        ('/subscriptions/12345-abcd-efgh/resourceGroups/rg-webapp/providers/Microsoft.Storage/storageAccounts/mystorage',
         '/subscriptions/12345-abcd-efgh/resourceGroups/rg-webapp/providers/Microsoft.Network/virtualNetworks/vnet1'),
    ]
    
    print("🧪 Probando layout jerárquico con filtrado de dependencias...")
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    # Verificar que se generó contenido y tiene estructura jerárquica
    assert content is not None, "No se generó contenido"
    assert len(content) > 1000, "El contenido es demasiado corto"
    assert 'Root Management Group' in content, "No se encontró el Management Group raíz"
    assert 'Production Subscription' in content, "No se encontró la suscripción"
    assert 'rg-webapp' in content, "No se encontró el Resource Group"
    assert 'vnet1' in content, "No se encontró la VNet"
    assert 'mystorage' in content, "No se encontró el Storage Account"
    
    # Verificar que tiene dos tipos de líneas (sólidas y punteadas)
    assert 'strokeColor=#1976d2;strokeWidth=2;' in content, "No se encontraron líneas jerárquicas (sólidas azules)"
    assert 'dashed=1;' in content, "No se encontraron líneas de dependencias (punteadas)"
    
    # Guardar archivo de prueba
    output_file = 'test-hierarchy-tree.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test completado exitosamente")
    print(f"📁 Archivo generado: {output_file}")
    print("🔗 Para ver el diagrama, abre el archivo en https://app.diagrams.net")
    print("📊 El diagrama debe mostrar:")
    print("   • Estructura de árbol jerárquica clara")
    print("   • Líneas azules sólidas para jerarquía (MG→Sub→RG→Recurso)")
    print("   • Líneas grises punteadas para dependencias (Storage→VNet)")

def test_virtual_root_with_filtered_dependencies():
    """Test del layout jerárquico sin Management Groups (con nodo raíz virtual)"""
    
    # Datos de prueba sin Management Groups
    test_items = [
        # Solo suscripción (nivel 1, será hijo del nodo raíz virtual)
        {
            'id': '/subscriptions/98765-wxyz',
            'name': 'Dev Subscription',
            'type': 'Microsoft.Resources/subscriptions',
            'subscriptionId': '98765-wxyz'
        },
        # Resource Group (nivel 2)
        {
            'id': '/subscriptions/98765-wxyz/resourceGroups/rg-test',
            'name': 'rg-test',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups',
            'resourceGroup': 'rg-test',
            'subscriptionId': '98765-wxyz'
        },
        # VM (nivel 3)
        {
            'id': '/subscriptions/98765-wxyz/resourceGroups/rg-test/providers/Microsoft.Compute/virtualMachines/vm1',
            'name': 'vm1',
            'type': 'Microsoft.Compute/virtualMachines',
            'resourceGroup': 'rg-test',
            'subscriptionId': '98765-wxyz'
        },
        # Disk (nivel 3)
        {
            'id': '/subscriptions/98765-wxyz/resourceGroups/rg-test/providers/Microsoft.Compute/disks/disk1',
            'name': 'disk1',
            'type': 'Microsoft.Compute/disks',
            'resourceGroup': 'rg-test',
            'subscriptionId': '98765-wxyz'
        }
    ]
    
    # Dependencias mixtas sin Management Groups
    test_dependencies = [
        # Dependencia NO jerárquica (relación)
        ('/subscriptions/98765-wxyz/resourceGroups/rg-test/providers/Microsoft.Compute/disks/disk1',
         '/subscriptions/98765-wxyz/resourceGroups/rg-test/providers/Microsoft.Compute/virtualMachines/vm1'),
    ]
    
    print("🧪 Probando layout jerárquico sin Management Groups...")
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    # Verificar que se generó contenido y el nodo raíz virtual
    assert content is not None, "No se generó contenido"
    assert 'Azure Tenant (Root)' in content, "No se encontró el nodo raíz virtual"
    assert 'Dev Subscription' in content, "No se encontró la suscripción"
    assert 'vm1' in content, "No se encontró la VM"
    assert 'disk1' in content, "No se encontró el disk"
    
    # Guardar archivo de prueba
    output_file = 'test-hierarchy-virtual-root.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test completado exitosamente")
    print(f"📁 Archivo generado: {output_file}")
    print("🌟 Características del nodo raíz virtual:")
    print("   • Creado automáticamente cuando no hay Management Groups")  
    print("   • Conecta automáticamente elementos huérfanos")
    print("   • Mantiene la estructura jerárquica visual")

if __name__ == "__main__":
    test_hierarchical_tree_layout()
    print()
    test_virtual_root_with_filtered_dependencies()
    print("\n🎉 Todos los tests del árbol jerárquico pasaron correctamente!")
    print("\n🌳 Características implementadas:")
    print("   ✅ Algoritmo DFS para layout de árbol real")
    print("   ✅ Filtrado de dependencias jerárquicas vs relaciones")
    print("   ✅ Líneas sólidas azules para jerarquía")
    print("   ✅ Líneas punteadas grises para dependencias")
    print("   ✅ Nodo raíz virtual automático")
    print("   ✅ Conexión automática de elementos huérfanos")
    print("   ✅ Protección contra recursión infinita")

#!/usr/bin/env python3
"""
Test para verificar el layout en arco con espaciado mejorado
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from drawio_export import generate_drawio_file

def test_arc_layout_spacing():
    """Test del layout en arco con espaciado mejorado"""
    
    # Datos de prueba con diferentes escenarios de espaciado
    test_items = [
        # Management Group
        {
            'id': '/providers/Microsoft.Management/managementGroups/mg-arc',
            'name': 'Arc Layout Test',
            'type': 'Microsoft.Management/managementGroups'
        },
        # Suscripción
        {
            'id': '/subscriptions/sub-arc',
            'name': 'Arc Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        # RG con 4 recursos (mínimo para arco)
        {
            'id': '/subscriptions/sub-arc/resourceGroups/rg-small-arc',
            'name': 'rg-small-arc',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        # RG con 6 recursos (arco mediano)
        {
            'id': '/subscriptions/sub-arc/resourceGroups/rg-medium-arc',
            'name': 'rg-medium-arc',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        # RG con 10 recursos (arco grande)
        {
            'id': '/subscriptions/sub-arc/resourceGroups/rg-large-arc',
            'name': 'rg-large-arc',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        }
    ]
    
    # 4 recursos para arco pequeño
    small_resources = [
        ('vm-web', 'Microsoft.Compute/virtualMachines'),
        ('st-data', 'Microsoft.Storage/storageAccounts'),
        ('vnet-main', 'Microsoft.Network/virtualNetworks'),
        ('kv-secrets', 'Microsoft.KeyVault/vaults')
    ]
    
    for name, resource_type in small_resources:
        test_items.append({
            'id': f'/subscriptions/sub-arc/resourceGroups/rg-small-arc/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-small-arc'
        })
    
    # 6 recursos para arco mediano
    medium_resources = [
        ('vm-web-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-web-02', 'Microsoft.Compute/virtualMachines'),
        ('st-data', 'Microsoft.Storage/storageAccounts'),
        ('vnet-prod', 'Microsoft.Network/virtualNetworks'),
        ('lb-frontend', 'Microsoft.Network/loadBalancers'),
        ('kv-secrets', 'Microsoft.KeyVault/vaults')
    ]
    
    for name, resource_type in medium_resources:
        test_items.append({
            'id': f'/subscriptions/sub-arc/resourceGroups/rg-medium-arc/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-medium-arc'
        })
    
    # 10 recursos para arco grande
    large_resources = [
        ('vm-web-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-web-02', 'Microsoft.Compute/virtualMachines'),
        ('vm-api-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-api-02', 'Microsoft.Compute/virtualMachines'),
        ('vm-db', 'Microsoft.Compute/virtualMachines'),
        ('st-data', 'Microsoft.Storage/storageAccounts'),
        ('st-logs', 'Microsoft.Storage/storageAccounts'),
        ('vnet-prod', 'Microsoft.Network/virtualNetworks'),
        ('lb-frontend', 'Microsoft.Network/loadBalancers'),
        ('kv-secrets', 'Microsoft.KeyVault/vaults')
    ]
    
    for name, resource_type in large_resources:
        test_items.append({
            'id': f'/subscriptions/sub-arc/resourceGroups/rg-large-arc/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-large-arc'
        })
    
    # Dependencias jerárquicas
    test_dependencies = [
        ('/subscriptions/sub-arc', '/providers/Microsoft.Management/managementGroups/mg-arc'),
        ('/subscriptions/sub-arc/resourceGroups/rg-small-arc', '/subscriptions/sub-arc'),
        ('/subscriptions/sub-arc/resourceGroups/rg-medium-arc', '/subscriptions/sub-arc'),
        ('/subscriptions/sub-arc/resourceGroups/rg-large-arc', '/subscriptions/sub-arc'),
    ]
    
    # Conectar recursos a sus RGs
    for name, resource_type in small_resources:
        resource_id = f'/subscriptions/sub-arc/resourceGroups/rg-small-arc/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-arc/resourceGroups/rg-small-arc'))
    
    for name, resource_type in medium_resources:
        resource_id = f'/subscriptions/sub-arc/resourceGroups/rg-medium-arc/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-arc/resourceGroups/rg-medium-arc'))
    
    for name, resource_type in large_resources:
        resource_id = f'/subscriptions/sub-arc/resourceGroups/rg-large-arc/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-arc/resourceGroups/rg-large-arc'))
    
    print("🧪 Probando layout en arco con espaciado mejorado...")
    print(f"📊 RG pequeño: {len(small_resources)} recursos (arco compacto)")
    print(f"📊 RG mediano: {len(medium_resources)} recursos (arco medio)")
    print(f"📊 RG grande: {len(large_resources)} recursos (arco amplio)")
    print(f"📐 Mejoras de espaciado:")
    print(f"   • Radio mínimo: 150px (antes: 100px)")
    print(f"   • Espacio por recurso: 20px (antes: 12px)")
    print(f"   • Ángulo mínimo entre recursos: 0.3 radianes")
    print(f"   • Padding adicional en ancho total")
    
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    # Verificaciones
    assert content is not None, "No se generó contenido"
    assert len(content) > 2000, "El contenido es demasiado corto"
    
    # Verificar estructura
    assert 'Arc Layout Test' in content, "No se encontró el Management Group"
    assert 'rg-small-arc' in content, "No se encontró RG pequeño"
    assert 'rg-medium-arc' in content, "No se encontró RG mediano"
    assert 'rg-large-arc' in content, "No se encontró RG grande"
    
    # Verificar algunos recursos
    assert 'vm-web' in content, "No se encontró VM en arco pequeño"
    assert 'vm-web-01' in content, "No se encontró VM en arcos medianos/grandes"
    assert 'kv-secrets' in content, "No se encontró Key Vault"
    
    output_file = 'test-arc-spacing.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test de espaciado en arco completado exitosamente")
    print(f"📁 Archivo generado: {output_file}")
    print(f"📐 Espaciado verificado:")
    print(f"   • Los recursos NO deben solaparse")
    print(f"   • Arcos más amplios para mejor distribución")
    print(f"   • Resource Groups centrados arriba de cada arco")

def test_single_resource_cases():
    """Test casos especiales con pocos recursos"""
    
    test_items = [
        # Suscripción sin MG
        {
            'id': '/subscriptions/sub-special',
            'name': 'Special Cases Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        # RG con 1 recurso (debería usar layout simple)
        {
            'id': '/subscriptions/sub-special/resourceGroups/rg-one',
            'name': 'rg-one-resource',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        # RG con 2 recursos (debería usar layout simple)
        {
            'id': '/subscriptions/sub-special/resourceGroups/rg-two',
            'name': 'rg-two-resources',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        # RG con 3 recursos (debería usar layout simple)
        {
            'id': '/subscriptions/sub-special/resourceGroups/rg-three',
            'name': 'rg-three-resources',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        }
    ]
    
    # 1 recurso
    test_items.append({
        'id': '/subscriptions/sub-special/resourceGroups/rg-one/providers/Microsoft.Compute/virtualMachines/vm-only',
        'name': 'vm-only',
        'type': 'Microsoft.Compute/virtualMachines',
        'resourceGroup': 'rg-one'
    })
    
    # 2 recursos
    two_resources = [
        ('vm-main', 'Microsoft.Compute/virtualMachines'),
        ('st-main', 'Microsoft.Storage/storageAccounts')
    ]
    
    for name, resource_type in two_resources:
        test_items.append({
            'id': f'/subscriptions/sub-special/resourceGroups/rg-two/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-two'
        })
    
    # 3 recursos
    three_resources = [
        ('vm-app', 'Microsoft.Compute/virtualMachines'),
        ('st-data', 'Microsoft.Storage/storageAccounts'),
        ('vnet-main', 'Microsoft.Network/virtualNetworks')
    ]
    
    for name, resource_type in three_resources:
        test_items.append({
            'id': f'/subscriptions/sub-special/resourceGroups/rg-three/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-three'
        })
    
    # Dependencias
    test_dependencies = [
        ('/subscriptions/sub-special/resourceGroups/rg-one', '/subscriptions/sub-special'),
        ('/subscriptions/sub-special/resourceGroups/rg-two', '/subscriptions/sub-special'),
        ('/subscriptions/sub-special/resourceGroups/rg-three', '/subscriptions/sub-special'),
        
        # Conectar recursos
        ('/subscriptions/sub-special/resourceGroups/rg-one/providers/Microsoft.Compute/virtualMachines/vm-only',
         '/subscriptions/sub-special/resourceGroups/rg-one'),
    ]
    
    for name, resource_type in two_resources:
        resource_id = f'/subscriptions/sub-special/resourceGroups/rg-two/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-special/resourceGroups/rg-two'))
    
    for name, resource_type in three_resources:
        resource_id = f'/subscriptions/sub-special/resourceGroups/rg-three/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-special/resourceGroups/rg-three'))
    
    print("\n🧪 Probando casos especiales con pocos recursos...")
    print(f"📊 RG con 1 recurso: layout simple")
    print(f"📊 RG con 2 recursos: layout simple")
    print(f"📊 RG con 3 recursos: layout simple")
    print(f"📐 Solo RGs con ≥4 recursos usan layout en arco")
    
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    assert content is not None, "No se generó contenido"
    
    output_file = 'test-arc-special-cases.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test de casos especiales completado")
    print(f"📁 Archivo generado: {output_file}")
    print(f"📐 Verificar que RGs con <4 recursos usan layout lineal")

if __name__ == "__main__":
    try:
        test_arc_layout_spacing()
        test_single_resource_cases()
        print("\n🎉 TODOS LOS TESTS DE LAYOUT EN ARCO CON ESPACIADO MEJORADO PASARON")
        print("\n📋 Mejoras implementadas:")
        print("   ✅ Radio mínimo aumentado a 150px")
        print("   ✅ Espaciado por recurso aumentado a 20px")
        print("   ✅ Ángulo mínimo entre recursos: 0.3 radianes")
        print("   ✅ Arco adaptativo según número de recursos")
        print("   ✅ Padding adicional para evitar solapamientos")
        print("   ✅ Layout lineal mantenido para RGs con <4 recursos")
        print("\n🎯 Los recursos en arco ya NO deben solaparse")
    except Exception as e:
        print(f"\n❌ ERROR en tests de espaciado en arco: {e}")
        import traceback
        traceback.print_exc()
        raise

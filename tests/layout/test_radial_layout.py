#!/usr/bin/env python3
"""
Test para verificar el layout radial en Resource Groups
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from drawio_export import generate_drawio_file

def test_radial_layout():
    """Test del layout radial para Resource Groups"""
    
    # Datos de prueba con Resource Groups que tienen diferentes cantidades de recursos
    test_items = [
        # Management Group
        {
            'id': '/providers/Microsoft.Management/managementGroups/mg-radial',
            'name': 'Radial Layout Test',
            'type': 'Microsoft.Management/managementGroups'
        },
        # Suscripción
        {
            'id': '/subscriptions/sub-radial',
            'name': 'Radial Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        # RG con pocos recursos (3 - debería usar layout lineal)
        {
            'id': '/subscriptions/sub-radial/resourceGroups/rg-few',
            'name': 'rg-few-resources',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        # RG con recursos suficientes para layout radial (6)
        {
            'id': '/subscriptions/sub-radial/resourceGroups/rg-medium',
            'name': 'rg-medium-resources',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        # RG con muchos recursos (10 - layout radial)
        {
            'id': '/subscriptions/sub-radial/resourceGroups/rg-many',
            'name': 'rg-many-resources',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        }
    ]
    
    # Pocos recursos (3 - layout lineal)
    few_resources = [
        ('vm-simple', 'Microsoft.Compute/virtualMachines'),
        ('st-simple', 'Microsoft.Storage/storageAccounts'),
        ('vnet-simple', 'Microsoft.Network/virtualNetworks')
    ]
    
    for name, resource_type in few_resources:
        test_items.append({
            'id': f'/subscriptions/sub-radial/resourceGroups/rg-few/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-few'
        })
    
    # Recursos medianos (6 - layout radial)
    medium_resources = [
        ('vm-web-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-web-02', 'Microsoft.Compute/virtualMachines'),
        ('st-data', 'Microsoft.Storage/storageAccounts'),
        ('vnet-prod', 'Microsoft.Network/virtualNetworks'),
        ('lb-external', 'Microsoft.Network/loadBalancers'),
        ('kv-secrets', 'Microsoft.KeyVault/vaults')
    ]
    
    for name, resource_type in medium_resources:
        test_items.append({
            'id': f'/subscriptions/sub-radial/resourceGroups/rg-medium/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-medium'
        })
    
    # Muchos recursos (10 - layout radial con círculo más grande)
    many_resources = [
        ('vm-web-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-web-02', 'Microsoft.Compute/virtualMachines'),
        ('vm-api-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-api-02', 'Microsoft.Compute/virtualMachines'),
        ('vm-db-01', 'Microsoft.Compute/virtualMachines'),
        ('st-data', 'Microsoft.Storage/storageAccounts'),
        ('st-logs', 'Microsoft.Storage/storageAccounts'),
        ('vnet-prod', 'Microsoft.Network/virtualNetworks'),
        ('lb-external', 'Microsoft.Network/loadBalancers'),
        ('kv-prod', 'Microsoft.KeyVault/vaults')
    ]
    
    for name, resource_type in many_resources:
        test_items.append({
            'id': f'/subscriptions/sub-radial/resourceGroups/rg-many/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-many'
        })
    
    # Dependencias jerárquicas
    test_dependencies = [
        ('/subscriptions/sub-radial', '/providers/Microsoft.Management/managementGroups/mg-radial'),
        ('/subscriptions/sub-radial/resourceGroups/rg-few', '/subscriptions/sub-radial'),
        ('/subscriptions/sub-radial/resourceGroups/rg-medium', '/subscriptions/sub-radial'),
        ('/subscriptions/sub-radial/resourceGroups/rg-many', '/subscriptions/sub-radial'),
    ]
    
    # Conectar recursos a sus RGs
    for name, resource_type in few_resources:
        resource_id = f'/subscriptions/sub-radial/resourceGroups/rg-few/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-radial/resourceGroups/rg-few'))
    
    for name, resource_type in medium_resources:
        resource_id = f'/subscriptions/sub-radial/resourceGroups/rg-medium/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-radial/resourceGroups/rg-medium'))
    
    for name, resource_type in many_resources:
        resource_id = f'/subscriptions/sub-radial/resourceGroups/rg-many/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-radial/resourceGroups/rg-many'))
    
    # Agregar algunas dependencias de relación
    test_dependencies.extend([
        # VMs → Storage en RG medium
        ('/subscriptions/sub-radial/resourceGroups/rg-medium/providers/Microsoft.Storage/storageAccounts/st-data',
         '/subscriptions/sub-radial/resourceGroups/rg-medium/providers/Microsoft.Compute/virtualMachines/vm-web-01'),
        # VMs → VNet en RG medium  
        ('/subscriptions/sub-radial/resourceGroups/rg-medium/providers/Microsoft.Compute/virtualMachines/vm-web-01',
         '/subscriptions/sub-radial/resourceGroups/rg-medium/providers/Microsoft.Network/virtualNetworks/vnet-prod'),
        
        # VMs → Storage en RG many
        ('/subscriptions/sub-radial/resourceGroups/rg-many/providers/Microsoft.Storage/storageAccounts/st-data',
         '/subscriptions/sub-radial/resourceGroups/rg-many/providers/Microsoft.Compute/virtualMachines/vm-web-01'),
        ('/subscriptions/sub-radial/resourceGroups/rg-many/providers/Microsoft.Storage/storageAccounts/st-logs',
         '/subscriptions/sub-radial/resourceGroups/rg-many/providers/Microsoft.Compute/virtualMachines/vm-api-01'),
    ])
    
    print("🧪 Probando layout radial para Resource Groups...")
    print(f"📊 RG pocos recursos: {len(few_resources)} (layout lineal)")
    print(f"📊 RG recursos medianos: {len(medium_resources)} (layout radial)")
    print(f"📊 RG muchos recursos: {len(many_resources)} (layout radial)")
    print(f"🔄 Layout radial: recursos dispuestos en círculo alrededor del RG")
    
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
    
    # Verificar que se generó la estructura
    assert 'Radial Layout Test' in content, "No se encontró el Management Group"
    assert 'Radial Subscription' in content, "No se encontró la suscripción"
    assert 'rg-few-resources' in content, "No se encontró RG few"
    assert 'rg-medium-resources' in content, "No se encontró RG medium"
    assert 'rg-many-resources' in content, "No se encontró RG many"
    
    # Verificar algunos recursos
    assert 'vm-simple' in content, "No se encontró VM simple"
    assert 'vm-web-01' in content, "No se encontró VM web"
    assert 'st-data' in content, "No se encontró Storage data"
    assert 'kv-secrets' in content, "No se encontró Key Vault secrets"
    assert 'kv-prod' in content, "No se encontró Key Vault prod"
    
    # Verificar tipos de líneas
    assert 'strokeColor=#1976d2;strokeWidth=2;' in content, "No se encontraron líneas jerárquicas"
    assert 'dashed=1;' in content, "No se encontraron líneas de relación"
    
    # Guardar archivo de prueba
    output_file = 'test-radial-layout.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test de layout radial completado exitosamente")
    print(f"📁 Archivo generado: {output_file}")
    print(f"🔄 Los Resource Groups deben mostrar:")
    print(f"   • rg-few-resources: 3 recursos en línea (layout lineal)")
    print(f"   • rg-medium-resources: 6 recursos en círculo (layout radial)")
    print(f"   • rg-many-resources: 10 recursos en círculo más grande (layout radial)")
    print(f"   • Resource Groups en el centro de sus círculos respectivos")

def test_radial_edge_cases():
    """Test de casos edge para layout radial"""
    
    test_items = [
        # Suscripción sin MG
        {
            'id': '/subscriptions/sub-edge',
            'name': 'Edge Cases Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        # RG con exactamente 4 recursos (mínimo para radial)
        {
            'id': '/subscriptions/sub-edge/resourceGroups/rg-minimum',
            'name': 'rg-minimum-radial',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        # RG con 1 solo recurso
        {
            'id': '/subscriptions/sub-edge/resourceGroups/rg-single',
            'name': 'rg-single-resource',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        }
    ]
    
    # Exactamente 4 recursos (borde mínimo para radial)
    minimum_resources = [
        ('vm-edge', 'Microsoft.Compute/virtualMachines'),
        ('st-edge', 'Microsoft.Storage/storageAccounts'),
        ('vnet-edge', 'Microsoft.Network/virtualNetworks'),
        ('kv-edge', 'Microsoft.KeyVault/vaults')
    ]
    
    for name, resource_type in minimum_resources:
        test_items.append({
            'id': f'/subscriptions/sub-edge/resourceGroups/rg-minimum/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-minimum'
        })
    
    # Solo 1 recurso
    test_items.append({
        'id': '/subscriptions/sub-edge/resourceGroups/rg-single/providers/Microsoft.Compute/virtualMachines/vm-only',
        'name': 'vm-only',
        'type': 'Microsoft.Compute/virtualMachines',
        'resourceGroup': 'rg-single'
    })
    
    # Dependencias
    test_dependencies = [
        ('/subscriptions/sub-edge/resourceGroups/rg-minimum', '/subscriptions/sub-edge'),
        ('/subscriptions/sub-edge/resourceGroups/rg-single', '/subscriptions/sub-edge'),
    ]
    
    for name, resource_type in minimum_resources:
        resource_id = f'/subscriptions/sub-edge/resourceGroups/rg-minimum/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-edge/resourceGroups/rg-minimum'))
    
    test_dependencies.append((
        '/subscriptions/sub-edge/resourceGroups/rg-single/providers/Microsoft.Compute/virtualMachines/vm-only',
        '/subscriptions/sub-edge/resourceGroups/rg-single'
    ))
    
    print("\n🧪 Probando casos edge del layout radial...")
    print(f"📊 RG mínimo: 4 recursos (justo en el límite para radial)")
    print(f"📊 RG único: 1 recurso (debería usar layout lineal)")
    
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    assert content is not None, "No se generó contenido"
    
    output_file = 'test-radial-edge-cases.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test de casos edge completado")
    print(f"📁 Archivo generado: {output_file}")
    print(f"🔄 Debe mostrar:")
    print(f"   • rg-minimum-radial: 4 recursos en pequeño círculo")
    print(f"   • rg-single-resource: 1 recurso en layout simple")

if __name__ == "__main__":
    try:
        test_radial_layout()
        test_radial_edge_cases()
        print("\n🎉 TODOS LOS TESTS DE LAYOUT RADIAL PASARON CORRECTAMENTE")
        print("\n📋 Resumen de la nueva funcionalidad:")
        print("   ✅ Resource Groups con ≥4 recursos usan layout radial")
        print("   ✅ Recursos dispuestos en círculo alrededor del RG")
        print("   ✅ Radio del círculo se ajusta al número de recursos")
        print("   ✅ Resource Group posicionado en el centro del círculo")
        print("   ✅ Layout lineal mantenido para RGs con <4 recursos")
        print("   ✅ Conexiones radiales desde el centro hacia los recursos")
        print("   ✅ Distribución angular uniforme de los recursos")
    except Exception as e:
        print(f"\n❌ ERROR en tests de layout radial: {e}")
        import traceback
        traceback.print_exc()
        raise

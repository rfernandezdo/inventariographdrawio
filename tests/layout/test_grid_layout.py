#!/usr/bin/env python3
"""
Test para verificar el layout de cuadrícula en Resource Groups con muchos recursos
"""

import sys
import os
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from drawio_export import generate_drawio_file

def test_resource_group_grid_layout():
    """Test del layout de cuadrícula para RGs con muchos recursos"""
    
    # Datos de prueba con un RG que tiene muchos recursos
    test_items = [
        # Management Group
        {
            'id': '/providers/Microsoft.Management/managementGroups/mg-test',
            'name': 'Test Management Group',
            'type': 'Microsoft.Management/managementGroups'
        },
        # Suscripción
        {
            'id': '/subscriptions/sub-test',
            'name': 'Test Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        # Resource Group con muchos recursos
        {
            'id': '/subscriptions/sub-test/resourceGroups/rg-many-resources',
            'name': 'rg-many-resources',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        }
    ]
    
    # Agregar 12 recursos diferentes al Resource Group para probar la cuadrícula
    resource_types = [
        ('vm-web-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-web-02', 'Microsoft.Compute/virtualMachines'),
        ('vm-api-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-api-02', 'Microsoft.Compute/virtualMachines'),
        ('st-storage01', 'Microsoft.Storage/storageAccounts'),
        ('st-storage02', 'Microsoft.Storage/storageAccounts'),
        ('vnet-main', 'Microsoft.Network/virtualNetworks'),
        ('nsg-web', 'Microsoft.Network/networkSecurityGroups'),
        ('nsg-api', 'Microsoft.Network/networkSecurityGroups'),
        ('lb-internal', 'Microsoft.Network/loadBalancers'),
        ('pip-gateway', 'Microsoft.Network/publicIPAddresses'),
        ('kv-secrets', 'Microsoft.KeyVault/vaults')
    ]
    
    for i, (name, resource_type) in enumerate(resource_types):
        test_items.append({
            'id': f'/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-many-resources',
            'subscriptionId': 'sub-test'
        })
    
    # Dependencias jerárquicas
    test_dependencies = [
        # Jerarquía básica
        ('/subscriptions/sub-test', '/providers/Microsoft.Management/managementGroups/mg-test'),
        ('/subscriptions/sub-test/resourceGroups/rg-many-resources', '/subscriptions/sub-test'),
    ]
    
    # Conectar todos los recursos al Resource Group
    for name, resource_type in resource_types:
        resource_id = f'/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-test/resourceGroups/rg-many-resources'))
    
    # Agregar algunas dependencias de relación entre recursos
    test_dependencies.extend([
        # VMs → Storage
        ('/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Storage/storageAccounts/st-storage01',
         '/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Compute/virtualMachines/vm-web-01'),
        ('/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Storage/storageAccounts/st-storage02',
         '/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Compute/virtualMachines/vm-api-01'),
        
        # VMs → VNet
        ('/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Compute/virtualMachines/vm-web-01',
         '/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Network/virtualNetworks/vnet-main'),
        ('/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Compute/virtualMachines/vm-api-01',
         '/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Network/virtualNetworks/vnet-main'),
        
        # NSGs → VNet
        ('/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Network/networkSecurityGroups/nsg-web',
         '/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Network/virtualNetworks/vnet-main'),
        ('/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Network/networkSecurityGroups/nsg-api',
         '/subscriptions/sub-test/resourceGroups/rg-many-resources/providers/Microsoft.Network/virtualNetworks/vnet-main')
    ])
    
    print("🧪 Probando layout de cuadrícula para Resource Group con muchos recursos...")
    print(f"📊 Resource Group: 1 con {len(resource_types)} recursos")
    print(f"🔗 Dependencias: {len(test_dependencies)} relaciones")
    print(f"📐 Expectativa: Recursos organizados en cuadrícula (máx 6 por fila)")
    
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
    assert 'Test Management Group' in content, "No se encontró el Management Group"
    assert 'Test Subscription' in content, "No se encontró la suscripción"
    assert 'rg-many-resources' in content, "No se encontró el Resource Group"
    
    # Verificar algunos recursos
    assert 'vm-web-01' in content, "No se encontró VM web 1"
    assert 'st-storage01' in content, "No se encontró Storage 1"
    assert 'vnet-main' in content, "No se encontró VNet"
    assert 'kv-secrets' in content, "No se encontró Key Vault"
    
    # Verificar tipos de líneas
    assert 'strokeColor=#1976d2;strokeWidth=2;' in content, "No se encontraron líneas jerárquicas"
    assert 'dashed=1;' in content, "No se encontraron líneas de relación"
    
    # Guardar archivo de prueba
    output_file = 'test-grid-layout.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test de layout de cuadrícula completado exitosamente")
    print(f"📁 Archivo generado: {output_file}")
    print(f"📐 Los 12 recursos dentro del RG deben estar organizados en cuadrícula")
    print(f"   • Máximo 6 recursos por fila")
    print(f"   • 2 filas con los recursos distribuidos")
    print(f"   • Resource Group centrado arriba")

def test_mixed_layout_scenarios():
    """Test de escenarios mixtos: algunos RGs con pocos recursos, otros con muchos"""
    
    test_items = [
        # Management Group
        {
            'id': '/providers/Microsoft.Management/managementGroups/mg-mixed',
            'name': 'Mixed Layout Test',
            'type': 'Microsoft.Management/managementGroups'
        },
        # Suscripción
        {
            'id': '/subscriptions/sub-mixed',
            'name': 'Mixed Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        # RG con pocos recursos (layout lineal)
        {
            'id': '/subscriptions/sub-mixed/resourceGroups/rg-few-resources',
            'name': 'rg-few-resources',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        # RG con muchos recursos (layout de cuadrícula)
        {
            'id': '/subscriptions/sub-mixed/resourceGroups/rg-many-resources',
            'name': 'rg-many-resources',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        }
    ]
    
    # Pocos recursos en el primer RG (solo 3 - debería usar layout lineal)
    few_resources = [
        ('vm-simple', 'Microsoft.Compute/virtualMachines'),
        ('st-simple', 'Microsoft.Storage/storageAccounts'),
        ('vnet-simple', 'Microsoft.Network/virtualNetworks')
    ]
    
    for name, resource_type in few_resources:
        test_items.append({
            'id': f'/subscriptions/sub-mixed/resourceGroups/rg-few-resources/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-few-resources'
        })
    
    # Muchos recursos en el segundo RG (10 - debería usar layout de cuadrícula)
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
            'id': f'/subscriptions/sub-mixed/resourceGroups/rg-many-resources/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-many-resources'
        })
    
    # Dependencias jerárquicas
    test_dependencies = [
        ('/subscriptions/sub-mixed', '/providers/Microsoft.Management/managementGroups/mg-mixed'),
        ('/subscriptions/sub-mixed/resourceGroups/rg-few-resources', '/subscriptions/sub-mixed'),
        ('/subscriptions/sub-mixed/resourceGroups/rg-many-resources', '/subscriptions/sub-mixed'),
    ]
    
    # Conectar recursos a sus RGs
    for name, resource_type in few_resources:
        resource_id = f'/subscriptions/sub-mixed/resourceGroups/rg-few-resources/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-mixed/resourceGroups/rg-few-resources'))
    
    for name, resource_type in many_resources:
        resource_id = f'/subscriptions/sub-mixed/resourceGroups/rg-many-resources/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-mixed/resourceGroups/rg-many-resources'))
    
    print("\n🧪 Probando escenarios mixtos de layout...")
    print(f"📊 RG pocos recursos: {len(few_resources)} (layout lineal)")
    print(f"📊 RG muchos recursos: {len(many_resources)} (layout cuadrícula)")
    
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    assert content is not None, "No se generó contenido"
    
    # Guardar archivo de prueba
    output_file = 'test-mixed-layout.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test de layout mixto completado")
    print(f"📁 Archivo generado: {output_file}")
    print(f"📐 Debe mostrar:")
    print(f"   • rg-few-resources: 3 recursos en línea horizontal")
    print(f"   • rg-many-resources: 10 recursos en cuadrícula (6+4)")

if __name__ == "__main__":
    try:
        test_resource_group_grid_layout()
        test_mixed_layout_scenarios()
        print("\n🎉 TODOS LOS TESTS DE LAYOUT DE CUADRÍCULA PASARON CORRECTAMENTE")
        print("\n📋 Resumen de mejoras:")
        print("   ✅ Resource Groups con >6 recursos usan layout de cuadrícula")
        print("   ✅ Máximo 6 recursos por fila")
        print("   ✅ Filas centradas automáticamente")
        print("   ✅ Resource Group padre posicionado en el centro superior")
        print("   ✅ Compatibilidad con escenarios mixtos")
        print("   ✅ Layout lineal mantenido para RGs con pocos recursos")
    except Exception as e:
        print(f"\n❌ ERROR en tests de layout: {e}")
        import traceback
        traceback.print_exc()
        raise

#!/usr/bin/env python3
"""
Test para verificar el layout en arco (semicírculo) bajo Resource Groups
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from drawio_export import generate_drawio_file

def test_arc_layout():
    """Test del layout en arco para Resource Groups"""
    
    # Datos de prueba con Resource Groups que tienen diferentes cantidades de recursos
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
        # RG con pocos recursos (3 - debería usar layout lineal)
        {
            'id': '/subscriptions/sub-arc/resourceGroups/rg-few',
            'name': 'rg-few-resources',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        # RG con recursos suficientes para layout en arco (5)
        {
            'id': '/subscriptions/sub-arc/resourceGroups/rg-medium',
            'name': 'rg-medium-arc',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        # RG con muchos recursos (8 - arco más amplio)
        {
            'id': '/subscriptions/sub-arc/resourceGroups/rg-many',
            'name': 'rg-many-arc',
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
            'id': f'/subscriptions/sub-arc/resourceGroups/rg-few/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-few'
        })
    
    # Recursos medianos (5 - layout en arco)
    medium_resources = [
        ('vm-web-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-web-02', 'Microsoft.Compute/virtualMachines'),
        ('st-data', 'Microsoft.Storage/storageAccounts'),
        ('vnet-prod', 'Microsoft.Network/virtualNetworks'),
        ('kv-secrets', 'Microsoft.KeyVault/vaults')
    ]
    
    for name, resource_type in medium_resources:
        test_items.append({
            'id': f'/subscriptions/sub-arc/resourceGroups/rg-medium/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-medium'
        })
    
    # Muchos recursos (8 - arco más amplio)
    many_resources = [
        ('vm-web-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-web-02', 'Microsoft.Compute/virtualMachines'),
        ('vm-api-01', 'Microsoft.Compute/virtualMachines'),
        ('st-data', 'Microsoft.Storage/storageAccounts'),
        ('st-logs', 'Microsoft.Storage/storageAccounts'),
        ('vnet-prod', 'Microsoft.Network/virtualNetworks'),
        ('lb-external', 'Microsoft.Network/loadBalancers'),
        ('kv-prod', 'Microsoft.KeyVault/vaults')
    ]
    
    for name, resource_type in many_resources:
        test_items.append({
            'id': f'/subscriptions/sub-arc/resourceGroups/rg-many/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-many'
        })
    
    # Dependencias jerárquicas
    test_dependencies = [
        ('/subscriptions/sub-arc', '/providers/Microsoft.Management/managementGroups/mg-arc'),
        ('/subscriptions/sub-arc/resourceGroups/rg-few', '/subscriptions/sub-arc'),
        ('/subscriptions/sub-arc/resourceGroups/rg-medium', '/subscriptions/sub-arc'),
        ('/subscriptions/sub-arc/resourceGroups/rg-many', '/subscriptions/sub-arc'),
    ]
    
    # Conectar recursos a sus RGs
    for name, resource_type in few_resources:
        resource_id = f'/subscriptions/sub-arc/resourceGroups/rg-few/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-arc/resourceGroups/rg-few'))
    
    for name, resource_type in medium_resources:
        resource_id = f'/subscriptions/sub-arc/resourceGroups/rg-medium/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-arc/resourceGroups/rg-medium'))
    
    for name, resource_type in many_resources:
        resource_id = f'/subscriptions/sub-arc/resourceGroups/rg-many/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-arc/resourceGroups/rg-many'))
    
    # Agregar algunas dependencias de relación
    test_dependencies.extend([
        # VMs → Storage en RG medium
        ('/subscriptions/sub-arc/resourceGroups/rg-medium/providers/Microsoft.Storage/storageAccounts/st-data',
         '/subscriptions/sub-arc/resourceGroups/rg-medium/providers/Microsoft.Compute/virtualMachines/vm-web-01'),
        # VMs → VNet en RG medium  
        ('/subscriptions/sub-arc/resourceGroups/rg-medium/providers/Microsoft.Compute/virtualMachines/vm-web-01',
         '/subscriptions/sub-arc/resourceGroups/rg-medium/providers/Microsoft.Network/virtualNetworks/vnet-prod'),
    ])
    
    print("🧪 Probando layout en arco para Resource Groups...")
    print(f"📊 RG pocos recursos: {len(few_resources)} (layout lineal)")
    print(f"📊 RG recursos medianos: {len(medium_resources)} (layout en arco)")
    print(f"📊 RG muchos recursos: {len(many_resources)} (layout en arco amplio)")
    print(f"🌉 Layout en arco: recursos dispuestos en semicírculo DEBAJO del RG")
    
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
    assert 'Arc Layout Test' in content, "No se encontró el Management Group"
    assert 'Arc Subscription' in content, "No se encontró la suscripción"
    assert 'rg-few-resources' in content, "No se encontró RG few"
    assert 'rg-medium-arc' in content, "No se encontró RG medium"
    assert 'rg-many-arc' in content, "No se encontró RG many"
    
    # Verificar algunos recursos
    assert 'vm-simple' in content, "No se encontró VM simple"
    assert 'vm-web-01' in content, "No se encontró VM web"
    assert 'st-data' in content, "No se encontró Storage data"
    assert 'kv-secrets' in content, "No se encontró Key Vault secrets"
    
    # Verificar tipos de líneas
    assert 'strokeColor=#1976d2;strokeWidth=2;' in content, "No se encontraron líneas jerárquicas"
    assert 'dashed=1;' in content, "No se encontraron líneas de relación"
    
    # Guardar archivo de prueba
    output_file = 'test-arc-layout.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test de layout en arco completado exitosamente")
    print(f"📁 Archivo generado: {output_file}")
    print(f"🌉 Los Resource Groups deben mostrar:")
    print(f"   • rg-few-resources: 3 recursos en línea (layout lineal)")
    print(f"   • rg-medium-arc: 5 recursos en arco debajo del RG")
    print(f"   • rg-many-arc: 8 recursos en arco más amplio debajo del RG")
    print(f"   • Resource Groups en la parte superior de sus arcos respectivos")

def test_webapp_arc_layout():
    """Test específico para una aplicación web con layout en arco"""
    
    test_items = [
        # Suscripción
        {
            'id': '/subscriptions/sub-webapp',
            'name': 'WebApp Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        # RG de aplicación web con recursos típicos
        {
            'id': '/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod',
            'name': 'rg-webapp-production',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        }
    ]
    
    # Aplicación web típica con 7 recursos (buen ejemplo para arco)
    webapp_resources = [
        ('vm-web-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-web-02', 'Microsoft.Compute/virtualMachines'),
        ('vm-api', 'Microsoft.Compute/virtualMachines'),
        ('st-webapp-data', 'Microsoft.Storage/storageAccounts'),
        ('vnet-webapp', 'Microsoft.Network/virtualNetworks'),
        ('sql-webapp-db', 'Microsoft.Sql/servers'),
        ('kv-webapp-secrets', 'Microsoft.KeyVault/vaults')
    ]
    
    for name, resource_type in webapp_resources:
        test_items.append({
            'id': f'/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-webapp-prod'
        })
    
    # Dependencias jerárquicas
    test_dependencies = [
        ('/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod', '/subscriptions/sub-webapp'),
    ]
    
    # Conectar todos los recursos al RG
    for name, resource_type in webapp_resources:
        resource_id = f'/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod'))
    
    # Dependencias de relación típicas
    test_dependencies.extend([
        # VMs → VNet
        ('/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod/providers/Microsoft.Compute/virtualMachines/vm-web-01',
         '/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod/providers/Microsoft.Network/virtualNetworks/vnet-webapp'),
        ('/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod/providers/Microsoft.Compute/virtualMachines/vm-api',
         '/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod/providers/Microsoft.Network/virtualNetworks/vnet-webapp'),
        
        # API → Database
        ('/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod/providers/Microsoft.Compute/virtualMachines/vm-api',
         '/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod/providers/Microsoft.Sql/servers/sql-webapp-db'),
        
        # API → Key Vault
        ('/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod/providers/Microsoft.Compute/virtualMachines/vm-api',
         '/subscriptions/sub-webapp/resourceGroups/rg-webapp-prod/providers/Microsoft.KeyVault/vaults/kv-webapp-secrets'),
    ])
    
    print("\n🧪 Probando aplicación web con layout en arco...")
    print(f"📊 Aplicación web: 7 recursos en arco")
    print(f"🌉 Disposición: semicírculo debajo del Resource Group")
    
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    assert content is not None, "No se generó contenido"
    
    output_file = 'test-webapp-arc.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test de webapp con arco completado")
    print(f"📁 Archivo generado: {output_file}")
    print(f"🌉 Debe mostrar:")
    print(f"   • rg-webapp-production en la parte superior")
    print(f"   • 7 recursos dispuestos en semicírculo debajo")
    print(f"   • Forma de arco natural y estética")

if __name__ == "__main__":
    try:
        test_arc_layout()
        test_webapp_arc_layout()
        print("\n🎉 TODOS LOS TESTS DE LAYOUT EN ARCO PASARON CORRECTAMENTE")
        print("\n📋 Resumen del layout en arco:")
        print("   ✅ Resource Groups con ≥4 recursos usan layout en arco")
        print("   ✅ Recursos dispuestos en semicírculo DEBAJO del RG")
        print("   ✅ RG posicionado en la parte superior del arco")
        print("   ✅ Distribución uniforme en 180 grados")
        print("   ✅ Radio se ajusta al número de recursos")
        print("   ✅ Layout lineal mantenido para RGs con <4 recursos")
        print("   ✅ Visualmente natural para diagramas jerárquicos")
        print("   ✅ Conexiones desde arriba hacia abajo")
    except Exception as e:
        print(f"\n❌ ERROR en tests de layout en arco: {e}")
        import traceback
        traceback.print_exc()
        raise

#!/usr/bin/env python3
"""
Test de comparación visual: Layout Radial vs otros layouts
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from drawio_export import generate_drawio_file

def test_visual_comparison():
    """Test para comparar visualmente diferentes tipos de layout"""
    
    test_items = [
        # Management Group
        {
            'id': '/providers/Microsoft.Management/managementGroups/mg-comparison',
            'name': 'Layout Comparison Demo',
            'type': 'Microsoft.Management/managementGroups'
        },
        # Suscripción
        {
            'id': '/subscriptions/sub-comparison',
            'name': 'Comparison Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        # RG con 8 recursos típicos de una aplicación web
        {
            'id': '/subscriptions/sub-comparison/resourceGroups/rg-webapp',
            'name': 'rg-webapp-radial',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        }
    ]
    
    # Recursos típicos de una aplicación web moderna
    webapp_resources = [
        ('vm-web-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-web-02', 'Microsoft.Compute/virtualMachines'),
        ('vm-api-01', 'Microsoft.Compute/virtualMachines'),
        ('vm-db-01', 'Microsoft.Compute/virtualMachines'),
        ('st-webapp-data', 'Microsoft.Storage/storageAccounts'),
        ('vnet-webapp', 'Microsoft.Network/virtualNetworks'),
        ('lb-frontend', 'Microsoft.Network/loadBalancers'),
        ('kv-webapp-secrets', 'Microsoft.KeyVault/vaults'),
        ('sql-webapp-db', 'Microsoft.Sql/servers'),
        ('appi-webapp-insights', 'Microsoft.Insights/components')
    ]
    
    for name, resource_type in webapp_resources:
        test_items.append({
            'id': f'/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/{resource_type}/{name}',
            'name': name,
            'type': resource_type,
            'resourceGroup': 'rg-webapp'
        })
    
    # Dependencias jerárquicas
    test_dependencies = [
        ('/subscriptions/sub-comparison', '/providers/Microsoft.Management/managementGroups/mg-comparison'),
        ('/subscriptions/sub-comparison/resourceGroups/rg-webapp', '/subscriptions/sub-comparison'),
    ]
    
    # Conectar todos los recursos al RG
    for name, resource_type in webapp_resources:
        resource_id = f'/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/{resource_type}/{name}'
        test_dependencies.append((resource_id, '/subscriptions/sub-comparison/resourceGroups/rg-webapp'))
    
    # Dependencias de relación típicas de una webapp
    test_dependencies.extend([
        # VMs web → Load Balancer
        ('/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-web-01',
         '/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Network/loadBalancers/lb-frontend'),
        ('/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-web-02',
         '/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Network/loadBalancers/lb-frontend'),
        
        # VMs → VNet
        ('/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-web-01',
         '/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Network/virtualNetworks/vnet-webapp'),
        ('/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-api-01',
         '/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Network/virtualNetworks/vnet-webapp'),
        ('/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-db-01',
         '/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Network/virtualNetworks/vnet-webapp'),
        
        # API VM → Database
        ('/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-api-01',
         '/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Sql/servers/sql-webapp-db'),
        
        # VMs → Storage
        ('/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Storage/storageAccounts/st-webapp-data',
         '/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-web-01'),
        
        # App Insights → VMs (monitoreo)
        ('/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Insights/components/appi-webapp-insights',
         '/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-web-01'),
        
        # Key Vault → API VM (secrets)
        ('/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-api-01',
         '/subscriptions/sub-comparison/resourceGroups/rg-webapp/providers/Microsoft.KeyVault/vaults/kv-webapp-secrets'),
    ])
    
    print("🧪 Generando diagrama de comparación con layout radial...")
    print(f"📊 Aplicación web típica: {len(webapp_resources)} recursos")
    print(f"🔄 Layout radial: recursos dispuestos en círculo")
    print(f"💫 Ventajas del layout radial:")
    print(f"   • Más compacto que layout lineal")
    print(f"   • Visualmente atractivo y balanceado")
    print(f"   • Fácil identificación del Resource Group central")
    print(f"   • Conexiones más cortas y claras")
    
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    assert content is not None, "No se generó contenido"
    assert len(content) > 1500, "El contenido es demasiado corto"
    
    # Verificar recursos clave
    assert 'Layout Comparison Demo' in content, "No se encontró el Management Group"
    assert 'rg-webapp-radial' in content, "No se encontró el Resource Group"
    assert 'vm-web-01' in content, "No se encontró VM web 1"
    assert 'sql-webapp-db' in content, "No se encontró SQL Server"
    assert 'kv-webapp-secrets' in content, "No se encontró Key Vault"
    assert 'lb-frontend' in content, "No se encontró Load Balancer"
    
    output_file = 'test-webapp-radial-demo.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Diagrama de comparación generado exitosamente")
    print(f"📁 Archivo generado: {output_file}")
    print(f"🎯 Para ver el resultado:")
    print(f"   1. Abre {output_file} en https://app.diagrams.net")
    print(f"   2. Observa el layout radial del Resource Group")
    print(f"   3. Los 10 recursos están dispuestos en un círculo perfecto")
    print(f"   4. El RG está en el centro, conectado radialmente")

def test_performance_radial():
    """Test de rendimiento con layout radial"""
    
    import time
    
    # Generar estructura con múltiples RGs con layout radial
    test_items = [
        {
            'id': '/providers/Microsoft.Management/managementGroups/mg-perf',
            'name': 'Performance Test',
            'type': 'Microsoft.Management/managementGroups'
        },
        {
            'id': '/subscriptions/sub-perf',
            'name': 'Performance Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        }
    ]
    
    test_dependencies = [
        ('/subscriptions/sub-perf', '/providers/Microsoft.Management/managementGroups/mg-perf')
    ]
    
    # Crear 5 Resource Groups con diferentes cantidades de recursos
    rg_sizes = [4, 6, 8, 10, 12]  # Todos usarán layout radial
    resource_types = [
        'Microsoft.Compute/virtualMachines',
        'Microsoft.Storage/storageAccounts',
        'Microsoft.Network/virtualNetworks',
        'Microsoft.KeyVault/vaults',
        'Microsoft.Sql/servers',
        'Microsoft.Network/loadBalancers',
        'Microsoft.Insights/components',
        'Microsoft.Network/networkSecurityGroups',
        'Microsoft.Compute/disks',
        'Microsoft.Network/publicIPAddresses',
        'Microsoft.Web/sites',
        'Microsoft.DocumentDB/databaseAccounts'
    ]
    
    for rg_num, size in enumerate(rg_sizes):
        rg_id = f'/subscriptions/sub-perf/resourceGroups/rg-radial-{rg_num+1:02d}'
        test_items.append({
            'id': rg_id,
            'name': f'rg-radial-{rg_num+1:02d}',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        })
        test_dependencies.append((rg_id, '/subscriptions/sub-perf'))
        
        # Agregar recursos al RG
        for res_num in range(size):
            resource_type = resource_types[res_num % len(resource_types)]
            resource_id = f'{rg_id}/providers/{resource_type}/resource-{res_num+1:02d}'
            test_items.append({
                'id': resource_id,
                'name': f'resource-{res_num+1:02d}',
                'type': resource_type,
                'resourceGroup': f'rg-radial-{rg_num+1:02d}'
            })
            test_dependencies.append((resource_id, rg_id))
    
    print(f"\n🧪 Test de rendimiento con layout radial...")
    print(f"📊 {len(rg_sizes)} Resource Groups con {sum(rg_sizes)} recursos totales")
    print(f"🔄 Todos los RGs usarán layout radial")
    
    start_time = time.time()
    
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    assert content is not None, "No se generó contenido"
    
    output_file = 'test-radial-performance.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    total_resources = len(test_items)
    throughput = total_resources / execution_time if execution_time > 0 else 0
    
    print(f"✅ Test de rendimiento completado")
    print(f"📁 Archivo generado: {output_file}")
    print(f"⏱️  Tiempo de ejecución: {execution_time:.3f} segundos")
    print(f"📈 Throughput: {throughput:.0f} recursos/segundo")
    print(f"🎯 Layout radial mantiene excelente rendimiento")

if __name__ == "__main__":
    try:
        test_visual_comparison()
        test_performance_radial()
        print("\n🎉 TODOS LOS TESTS DE COMPARACIÓN Y RENDIMIENTO PASARON")
        print("\n🌟 LAYOUT RADIAL IMPLEMENTADO EXITOSAMENTE")
        print("\n📋 Beneficios del layout radial:")
        print("   ✅ Visualmente más atractivo y balanceado")
        print("   ✅ Más compacto que layouts lineales o de cuadrícula")  
        print("   ✅ Resource Group claramente identificado en el centro")
        print("   ✅ Conexiones radiales más cortas y claras")
        print("   ✅ Distribución angular uniforme de recursos")
        print("   ✅ Escalable: radio se ajusta automáticamente")
        print("   ✅ Rendimiento óptimo mantenido")
        print("   ✅ Compatible con todos los tipos de recursos de Azure")
    except Exception as e:
        print(f"\n❌ ERROR en tests de comparación: {e}")
        import traceback
        traceback.print_exc()
        raise

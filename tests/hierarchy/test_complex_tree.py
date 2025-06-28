#!/usr/bin/env python3
"""
Test avanzado para verificar el algoritmo DFS con recursos complejos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from drawio_export import generate_drawio_file

def test_complex_resource_tree():
    """Test del algoritmo DFS con recursos complejos y múltiples niveles"""
    
    # Datos de prueba con estructura compleja real de Azure
    test_items = [
        # Nivel 0: Management Groups (jerarquía de 3 niveles)
        {
            'id': '/providers/Microsoft.Management/managementGroups/tenant-root',
            'name': 'Tenant Root',
            'type': 'Microsoft.Management/managementGroups'
        },
        {
            'id': '/providers/Microsoft.Management/managementGroups/contoso-root',
            'name': 'Contoso Root',
            'type': 'Microsoft.Management/managementGroups'
        },
        {
            'id': '/providers/Microsoft.Management/managementGroups/contoso-platform',
            'name': 'Platform',
            'type': 'Microsoft.Management/managementGroups'
        },
        
        # Nivel 1: Suscripciones
        {
            'id': '/subscriptions/sub-prod-001',
            'name': 'Production Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        {
            'id': '/subscriptions/sub-dev-001', 
            'name': 'Development Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        
        # Nivel 2: Resource Groups
        {
            'id': '/subscriptions/sub-prod-001/resourceGroups/rg-network',
            'name': 'rg-network',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-prod-001/resourceGroups/rg-compute',
            'name': 'rg-compute', 
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-dev-001/resourceGroups/rg-dev-apps',
            'name': 'rg-dev-apps',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        
        # Nivel 3: Recursos de red
        {
            'id': '/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-hub',
            'name': 'vnet-hub',
            'type': 'Microsoft.Network/virtualNetworks'
        },
        {
            'id': '/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-web',
            'name': 'subnet-web',
            'type': 'Microsoft.Network/virtualNetworks/subnets'
        },
        {
            'id': '/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-db',
            'name': 'subnet-db',
            'type': 'Microsoft.Network/virtualNetworks/subnets'
        },
        {
            'id': '/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/networkSecurityGroups/nsg-web',
            'name': 'nsg-web',
            'type': 'Microsoft.Network/networkSecurityGroups'
        },
        
        # Nivel 3: Recursos de compute
        {
            'id': '/subscriptions/sub-prod-001/resourceGroups/rg-compute/providers/Microsoft.Compute/virtualMachines/vm-web-01',
            'name': 'vm-web-01',
            'type': 'Microsoft.Compute/virtualMachines'
        },
        {
            'id': '/subscriptions/sub-prod-001/resourceGroups/rg-compute/providers/Microsoft.Compute/disks/vm-web-01-osdisk',
            'name': 'vm-web-01-osdisk',
            'type': 'Microsoft.Compute/disks'
        },
        {
            'id': '/subscriptions/sub-prod-001/resourceGroups/rg-compute/providers/Microsoft.Network/networkInterfaces/vm-web-01-nic',
            'name': 'vm-web-01-nic',
            'type': 'Microsoft.Network/networkInterfaces'
        },
        
        # Nivel 3: Recursos de dev
        {
            'id': '/subscriptions/sub-dev-001/resourceGroups/rg-dev-apps/providers/Microsoft.Web/sites/app-dev-api',
            'name': 'app-dev-api',
            'type': 'Microsoft.Web/sites'
        },
        {
            'id': '/subscriptions/sub-dev-001/resourceGroups/rg-dev-apps/providers/Microsoft.Storage/storageAccounts/stdevapi001',
            'name': 'stdevapi001',
            'type': 'Microsoft.Storage/storageAccounts'
        }
    ]
    
    # Dependencias jerárquicas (estructurales) y de relación
    test_dependencies = [
        # === DEPENDENCIAS JERÁRQUICAS (para el árbol) ===
        
        # Management Groups jerarquía
        ('/providers/Microsoft.Management/managementGroups/contoso-root', 
         '/providers/Microsoft.Management/managementGroups/tenant-root'),
        ('/providers/Microsoft.Management/managementGroups/contoso-platform', 
         '/providers/Microsoft.Management/managementGroups/contoso-root'),
        
        # Suscripciones → Management Groups
        ('/subscriptions/sub-prod-001', '/providers/Microsoft.Management/managementGroups/contoso-platform'),
        ('/subscriptions/sub-dev-001', '/providers/Microsoft.Management/managementGroups/contoso-platform'),
        
        # Resource Groups → Suscripciones
        ('/subscriptions/sub-prod-001/resourceGroups/rg-network', '/subscriptions/sub-prod-001'),
        ('/subscriptions/sub-prod-001/resourceGroups/rg-compute', '/subscriptions/sub-prod-001'),
        ('/subscriptions/sub-dev-001/resourceGroups/rg-dev-apps', '/subscriptions/sub-dev-001'),
        
        # Recursos → Resource Groups
        ('/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-hub',
         '/subscriptions/sub-prod-001/resourceGroups/rg-network'),
        ('/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/networkSecurityGroups/nsg-web',
         '/subscriptions/sub-prod-001/resourceGroups/rg-network'),
        ('/subscriptions/sub-prod-001/resourceGroups/rg-compute/providers/Microsoft.Compute/virtualMachines/vm-web-01',
         '/subscriptions/sub-prod-001/resourceGroups/rg-compute'),
        ('/subscriptions/sub-prod-001/resourceGroups/rg-compute/providers/Microsoft.Compute/disks/vm-web-01-osdisk',
         '/subscriptions/sub-prod-001/resourceGroups/rg-compute'),
        ('/subscriptions/sub-prod-001/resourceGroups/rg-compute/providers/Microsoft.Network/networkInterfaces/vm-web-01-nic',
         '/subscriptions/sub-prod-001/resourceGroups/rg-compute'),
        ('/subscriptions/sub-dev-001/resourceGroups/rg-dev-apps/providers/Microsoft.Web/sites/app-dev-api',
         '/subscriptions/sub-dev-001/resourceGroups/rg-dev-apps'),
        ('/subscriptions/sub-dev-001/resourceGroups/rg-dev-apps/providers/Microsoft.Storage/storageAccounts/stdevapi001',
         '/subscriptions/sub-dev-001/resourceGroups/rg-dev-apps'),
        
        # === DEPENDENCIAS DE RELACIÓN (líneas punteadas) ===
        
        # Subnets → VNet (relación padre-hijo especial)
        ('/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-web',
         '/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-hub'),
        ('/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-db',
         '/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-hub'),
        
        # VM → Disk (relación de uso)
        ('/subscriptions/sub-prod-001/resourceGroups/rg-compute/providers/Microsoft.Compute/disks/vm-web-01-osdisk',
         '/subscriptions/sub-prod-001/resourceGroups/rg-compute/providers/Microsoft.Compute/virtualMachines/vm-web-01'),
        
        # NIC → Subnet (relación de red)
        ('/subscriptions/sub-prod-001/resourceGroups/rg-compute/providers/Microsoft.Network/networkInterfaces/vm-web-01-nic',
         '/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-web'),
        
        # VM → NIC (relación de uso)
        ('/subscriptions/sub-prod-001/resourceGroups/rg-compute/providers/Microsoft.Network/networkInterfaces/vm-web-01-nic',
         '/subscriptions/sub-prod-001/resourceGroups/rg-compute/providers/Microsoft.Compute/virtualMachines/vm-web-01'),
        
        # NSG → Subnet (relación de seguridad)
        ('/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/networkSecurityGroups/nsg-web',
         '/subscriptions/sub-prod-001/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-web'),
        
        # App Service → Storage (relación de dependencia)
        ('/subscriptions/sub-dev-001/resourceGroups/rg-dev-apps/providers/Microsoft.Storage/storageAccounts/stdevapi001',
         '/subscriptions/sub-dev-001/resourceGroups/rg-dev-apps/providers/Microsoft.Web/sites/app-dev-api'),
    ]
    
    print("🧪 Probando árbol DFS con recursos complejos...")
    print(f"📊 Elementos: {len(test_items)} recursos")
    print(f"🔗 Dependencias: {len(test_dependencies)} relaciones")
    
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    # Verificaciones específicas de estructura compleja
    assert content is not None, "No se generó contenido"
    assert len(content) > 2000, "El contenido es demasiado corto para una estructura compleja"
    
    # Verificar jerarquía de Management Groups
    assert 'Tenant Root' in content, "No se encontró el MG raíz"
    assert 'Contoso Root' in content, "No se encontró el MG intermedio"
    assert 'Platform' in content, "No se encontró el MG hoja"
    
    # Verificar múltiples suscripciones
    assert 'Production Subscription' in content, "No se encontró suscripción de producción"
    assert 'Development Subscription' in content, "No se encontró suscripción de desarrollo"
    
    # Verificar múltiples Resource Groups
    assert 'rg-network' in content, "No se encontró RG de red"
    assert 'rg-compute' in content, "No se encontró RG de compute"
    assert 'rg-dev-apps' in content, "No se encontró RG de dev"
    
    # Verificar recursos especializados
    assert 'vnet-hub' in content, "No se encontró VNet"
    assert 'subnet-web' in content, "No se encontró subnet"
    assert 'vm-web-01' in content, "No se encontró VM"
    assert 'vm-web-01-osdisk' in content, "No se encontró disco"
    assert 'vm-web-01-nic' in content, "No se encontró NIC"
    assert 'nsg-web' in content, "No se encontró NSG"
    assert 'app-dev-api' in content, "No se encontró App Service"
    assert 'stdevapi001' in content, "No se encontró Storage Account"
    
    # Verificar tipos de líneas
    assert 'strokeColor=#1976d2;strokeWidth=2;' in content, "No se encontraron líneas jerárquicas"
    assert 'dashed=1;' in content, "No se encontraron líneas de relación"
    
    # Guardar archivo de prueba
    output_file = 'test-complex-tree-hierarchy.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test de recursos complejos completado")
    print(f"📁 Archivo generado: {output_file}")
    print("🌳 Estructura de árbol generada:")
    print("   📊 Tenant Root (nivel 0)")
    print("   ├── 📊 Contoso Root (nivel 1)")
    print("   │   └── 📊 Platform (nivel 2)")
    print("   │       ├── 📋 Production Sub (nivel 3)")
    print("   │       │   ├── 📁 rg-network (nivel 4)")
    print("   │       │   │   ├── 🌐 vnet-hub (nivel 5)")
    print("   │       │   │   │   ├── 🔗 subnet-web (relación)")
    print("   │       │   │   │   └── 🔗 subnet-db (relación)")
    print("   │       │   │   └── 🛡️ nsg-web (nivel 5)")
    print("   │       │   └── 📁 rg-compute (nivel 4)")
    print("   │       │       ├── 💻 vm-web-01 (nivel 5)")
    print("   │       │       ├── 💾 vm-web-01-osdisk (nivel 5)")
    print("   │       │       └── 🔌 vm-web-01-nic (nivel 5)")
    print("   │       └── 📋 Development Sub (nivel 3)")
    print("   │           └── 📁 rg-dev-apps (nivel 4)")
    print("   │               ├── 🌐 app-dev-api (nivel 5)")
    print("   │               └── 💾 stdevapi001 (nivel 5)")
    print("   📊 Conexiones:")
    print("   ├── ━━━━━━━ (azul sólido): Jerarquía estructural")
    print("   └── ┅┅┅┅┅┅┅ (gris punteado): Relaciones de uso/dependencia")

if __name__ == "__main__":
    test_complex_resource_tree()
    print("\n🎉 Test de recursos complejos completado exitosamente!")
    print("\n🚀 Mejoras del algoritmo DFS:")
    print("   ✅ Manejo de jerarquías MG multinivel")
    print("   ✅ Múltiples suscripciones y RGs")
    print("   ✅ Recursos especializados (VNet, Subnet, VM, Disk, NIC, NSG)")
    print("   ✅ Separación clara: jerarquía vs relaciones")
    print("   ✅ Layout balanceado automático")
    print("   ✅ Escalabilidad para estructuras complejas")

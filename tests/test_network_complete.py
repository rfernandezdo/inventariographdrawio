#!/usr/bin/env python3
"""
Test del modo network con datos más completos para mostrar la estructura
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.drawio_export import generate_drawio_file

# Datos más completos para mostrar mejor la estructura
test_items = [
    # Management Group
    {
        'id': '/providers/Microsoft.Management/managementGroups/mg-test',
        'name': 'Test Management Group',
        'type': 'Microsoft.Management/managementGroups'
    },
    # Suscripción
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012',
        'name': 'Test Subscription',
        'type': 'Microsoft.Resources/subscriptions'
    },
    # Resource Group
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network',
        'name': 'rg-network',
        'type': 'Microsoft.Resources/subscriptions/resourcegroups',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    },
    
    # Public IP
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/publicIPAddresses/pip-appgw',
        'name': 'pip-appgw',
        'type': 'Microsoft.Network/publicIPAddresses',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    },
    
    # Application Gateway
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/applicationGateways/appgw-main',
        'name': 'appgw-main',
        'type': 'Microsoft.Network/applicationGateways',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    },
    
    # VNet Principal
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main',
        'name': 'vnet-main',
        'type': 'Microsoft.Network/virtualNetworks',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    },
    
    # Subnet Web
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-web',
        'name': 'subnet-web',
        'type': 'Microsoft.Network/virtualNetworks/subnets',
        'vnetId': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    },
    
    # Subnet DB
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-db',
        'name': 'subnet-db',
        'type': 'Microsoft.Network/virtualNetworks/subnets',
        'vnetId': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    },
    
    # VM Web (en subnet-web)
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Compute/virtualMachines/vm-web-01',
        'name': 'vm-web-01',
        'type': 'Microsoft.Compute/virtualMachines',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012',
        'properties': {
            'subnet': {
                'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-web'
            }
        }
    },
    
    # VM Web 2 (en subnet-web)
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Compute/virtualMachines/vm-web-02',
        'name': 'vm-web-02',
        'type': 'Microsoft.Compute/virtualMachines',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012',
        'properties': {
            'subnet': {
                'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-web'
            }
        }
    },
    
    # VM Database (en subnet-db)
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Compute/virtualMachines/vm-db-01',
        'name': 'vm-db-01',
        'type': 'Microsoft.Compute/virtualMachines',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012',
        'properties': {
            'subnet': {
                'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-db'
            }
        }
    },
    
    # App Service (en subnet-web)
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Web/sites/app-web',
        'name': 'app-web',
        'type': 'Microsoft.Web/sites',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012',
        'properties': {
            'subnet': {
                'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-web'
            }
        }
    },
    
    # Load Balancer
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/loadBalancers/lb-web',
        'name': 'lb-web',
        'type': 'Microsoft.Network/loadBalancers',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    },
    
    # NSG
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/networkSecurityGroups/nsg-web',
        'name': 'nsg-web',
        'type': 'Microsoft.Network/networkSecurityGroups',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    }
]

print("🧪 Generando test completo del modo network...")
print(f"📊 Elementos de prueba: {len(test_items)}")

try:
    content = generate_drawio_file(
        test_items, 
        [],
        embed_data=False,
        include_ids=None,
        diagram_mode='network'
    )
    
    filename = 'test-network-complete.drawio'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Archivo generado: {filename}")
    print(f"📏 Tamaño: {len(content):,} caracteres")
    print(f"🌐 Abre en: https://app.diagrams.net")
    
    # Mostrar resumen de lo que debería verse
    print("\n📋 El diagrama debería mostrar:")
    print("   🔹 Governance (arriba): Management Group, Suscripción, Resource Group")
    print("   🔹 Internet Layer: Public IP")
    print("   🔹 Edge Layer: Application Gateway")
    print("   🔹 VNet Container: vnet-main con 2 subnets")
    print("     ├─ subnet-web: 3 recursos (2 VMs + 1 App Service)")
    print("     └─ subnet-db: 1 recurso (1 VM)")
    print("   🔹 Load Balancing: Load Balancer")
    print("   🔹 Network Security: NSG")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

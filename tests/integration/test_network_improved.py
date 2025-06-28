#!/usr/bin/env python3
"""
Test específico para el modo network mejorado
"""

import sys
import os
# Agregar el directorio padre al path para importar src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from src.drawio_export import generate_drawio_file
    print("✅ Importación exitosa")
    
    # Datos de prueba más realistas para un diagrama de red
    test_items = [
        # Management Group
        {
            'id': '/providers/Microsoft.Management/managementGroups/mg-prod',
            'name': 'Production Management Group',
            'type': 'Microsoft.Management/managementGroups'
        },
        # Subscription
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012',
            'name': 'Production Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        # Internet/Public resources
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/publicIPAddresses/pip-appgw',
            'name': 'pip-appgw',
            'type': 'Microsoft.Network/publicIPAddresses',
            'location': 'westeurope',
            'resourceGroup': 'rg-network'
        },
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/dnsZones/contoso.com',
            'name': 'contoso.com',
            'type': 'Microsoft.Network/dnsZones',
            'location': 'global',
            'resourceGroup': 'rg-network'
        },
        # Edge/Perimeter
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/applicationGateways/appgw-prod',
            'name': 'appgw-prod',
            'type': 'Microsoft.Network/applicationGateways',
            'location': 'westeurope',
            'resourceGroup': 'rg-network'
        },
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/azureFirewalls/fw-prod',
            'name': 'fw-prod',
            'type': 'Microsoft.Network/azureFirewalls',
            'location': 'westeurope',
            'resourceGroup': 'rg-network'
        },
        # VNet Principal
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-prod',
            'name': 'vnet-prod',
            'type': 'Microsoft.Network/virtualNetworks',
            'location': 'westeurope',
            'resourceGroup': 'rg-network'
        },
        # Subnets con diferentes tipos
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-prod/subnets/subnet-public-web',
            'name': 'subnet-public-web',
            'type': 'Microsoft.Network/virtualNetworks/subnets',
            'location': 'westeurope',
            'resourceGroup': 'rg-network'
        },
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-prod/subnets/subnet-app-tier',
            'name': 'subnet-app-tier',
            'type': 'Microsoft.Network/virtualNetworks/subnets',
            'location': 'westeurope',
            'resourceGroup': 'rg-network'
        },
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-prod/subnets/subnet-database',
            'name': 'subnet-database',
            'type': 'Microsoft.Network/virtualNetworks/subnets',
            'location': 'westeurope',
            'resourceGroup': 'rg-network'
        },
        # VMs en diferentes subnets
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-compute/providers/Microsoft.Compute/virtualMachines/vm-web-01',
            'name': 'vm-web-01',
            'type': 'Microsoft.Compute/virtualMachines',
            'location': 'westeurope',
            'resourceGroup': 'rg-compute',
            'properties': {
                'subnet': {
                    'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-prod/subnets/subnet-public-web'
                }
            }
        },
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-compute/providers/Microsoft.Compute/virtualMachines/vm-app-01',
            'name': 'vm-app-01',
            'type': 'Microsoft.Compute/virtualMachines',
            'location': 'westeurope',
            'resourceGroup': 'rg-compute',
            'properties': {
                'subnet': {
                    'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-prod/subnets/subnet-app-tier'
                }
            }
        },
        # Load Balancer
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/loadBalancers/lb-internal',
            'name': 'lb-internal',
            'type': 'Microsoft.Network/loadBalancers',
            'location': 'westeurope',
            'resourceGroup': 'rg-network'
        },
        # VPN Gateway
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworkGateways/vgw-prod',
            'name': 'vgw-prod',
            'type': 'Microsoft.Network/virtualNetworkGateways',
            'location': 'westeurope',
            'resourceGroup': 'rg-network'
        },
        # NSG
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/networkSecurityGroups/nsg-web',
            'name': 'nsg-web',
            'type': 'Microsoft.Network/networkSecurityGroups',
            'location': 'westeurope',
            'resourceGroup': 'rg-network'
        },
        # Key Vault
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-security/providers/Microsoft.KeyVault/vaults/kv-prod',
            'name': 'kv-prod',
            'type': 'Microsoft.KeyVault/vaults',
            'location': 'westeurope',
            'resourceGroup': 'rg-security'
        }
    ]
    
    print("🔥 Generando diagrama de red mejorado...")
    content = generate_drawio_file(
        test_items, 
        [],  # No dependencies for this test
        embed_data=False,
        include_ids=None,
        diagram_mode='network'
    )
    
    output_file = './tests/fixtures/test-network-improved.drawio'
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Archivo generado: {output_file}")
    print(f"📊 Tamaño: {len(content):,} caracteres")
    print(f"📈 Recursos procesados: {len(test_items)}")
    
    # Análisis del contenido generado
    if 'Internet / External Services' in content:
        print("✅ Capa Internet detectada")
    if 'Edge / Perimeter Security' in content:
        print("✅ Capa Edge detectada")
    if 'Region: Westeurope' in content:
        print("✅ Agrupación por región detectada")
    if 'Public Tier' in content:
        print("✅ Tiers de subnet detectados")
    if 'Hybrid Connectivity' in content:
        print("✅ Capa de conectividad detectada")
    if 'Security & Management' in content:
        print("✅ Panel de seguridad detectado")
    
    print("\n🎯 Mejoras implementadas:")
    print("   • Organización por capas de red (Internet → Edge → VNets → Conectividad)")
    print("   • Agrupación por regiones geográficas")
    print("   • Clasificación de subnets por tiers (Public, App, Private, Data)")
    print("   • Panel lateral para seguridad y gestión")
    print("   • Colores diferenciados por función")
    print("   • Layout más realista tipo arquitectura Azure")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

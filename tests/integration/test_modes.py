#!/usr/bin/env python3
"""
Script de prueba para verificar los modos de diagrama.
Crea datos de prueba para demostrar los diferentes layouts.
"""

import sys
import os

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.drawio_export import generate_drawio_file

# Datos de prueba simulando una infraestructura de Azure
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
        'type': 'Microsoft.Resources/subscriptions',
        'properties': {
            'managementGroupAncestorsChain': [
                {'id': '/providers/Microsoft.Management/managementGroups/mg-test'}
            ]
        }
    },
    # Resource Group
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network',
        'name': 'rg-network',
        'type': 'Microsoft.Resources/subscriptions/resourcegroups',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    },
    # VNet
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main',
        'name': 'vnet-main',
        'type': 'Microsoft.Network/virtualNetworks',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    },
    # Subnets
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-web',
        'name': 'subnet-web',
        'type': 'Microsoft.Network/virtualNetworks/subnets',
        'vnetId': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    },
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-db',
        'name': 'subnet-db',
        'type': 'Microsoft.Network/virtualNetworks/subnets',
        'vnetId': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main',
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
    # Public IP
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/publicIPAddresses/pip-appgw',
        'name': 'pip-appgw',
        'type': 'Microsoft.Network/publicIPAddresses',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    },
    # VM (con subnet asociada)
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Compute/virtualMachines/vm-web',
        'name': 'vm-web',
        'type': 'Microsoft.Compute/virtualMachines',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012',
        'properties': {
            'subnet': {
                'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-web'
            }
        }
    },
    # VM Database (con subnet asociada)
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Compute/virtualMachines/vm-db',
        'name': 'vm-db',
        'type': 'Microsoft.Compute/virtualMachines',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012',
        'properties': {
            'subnet': {
                'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-db'
            }
        }
    },
    # App Service (con subnet asociada)
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
    # NSG
    {
        'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/networkSecurityGroups/nsg-web',
        'name': 'nsg-web',
        'type': 'Microsoft.Network/networkSecurityGroups',
        'resourceGroup': 'rg-network',
        'subscriptionId': '12345678-1234-1234-1234-123456789012'
    }
]

test_dependencies = [
    # Dependencias jerárquicas
    ('/providers/Microsoft.Management/managementGroups/mg-test', '/subscriptions/12345678-1234-1234-1234-123456789012'),
    ('/subscriptions/12345678-1234-1234-1234-123456789012', '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network'),
]

def test_mode(mode_name):
    """Prueba un modo específico de diagrama"""
    print(f"\n=== Probando modo: {mode_name} ===")
    try:
        content = generate_drawio_file(
            test_items, 
            test_dependencies, 
            embed_data=False,  # Sin datos para que sea más rápido
            include_ids=None,
            diagram_mode=mode_name
        )
        filename = f"test-{mode_name}.drawio"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Archivo generado exitosamente: {filename}")
        print(f"  Tamaño del archivo: {len(content)} caracteres")
        return True
    except Exception as e:
        print(f"✗ Error al generar {mode_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Probando los modos de diagrama...")
    
    modes = ['infrastructure', 'components', 'network']
    results = {}
    
    for mode in modes:
        results[mode] = test_mode(mode)
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS:")
    for mode, success in results.items():
        status = "✓ ÉXITO" if success else "✗ FALLO"
        print(f"  {mode:15} : {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("\nArchivos generados:")
        for mode in modes:
            print(f"  - test-{mode}.drawio")
        print("\nPuedes abrir estos archivos en https://app.diagrams.net para ver los resultados.")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los errores arriba.")
        sys.exit(1)

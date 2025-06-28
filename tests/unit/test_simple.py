#!/usr/bin/env python3
"""
Prueba simple del modo network
"""

import sys
import os
# Agregar el directorio padre al path para importar src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from src.drawio_export import generate_drawio_file
    print("Importación exitosa")
    
    # Datos de prueba muy simples
    test_items = [
        {
            'id': '/subscriptions/12345/resourceGroups/rg1',
            'name': 'TestRG',
            'type': 'Microsoft.Resources/subscriptions/resourcegroups',
            'subscriptionId': '12345'
        },
        {
            'id': '/subscriptions/12345/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/vnet1',
            'name': 'vnet1',
            'type': 'Microsoft.Network/virtualNetworks',
            'resourceGroup': 'rg1',
            'subscriptionId': '12345'
        },
        {
            'id': '/subscriptions/12345/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/vnet1/subnets/subnet1',
            'name': 'subnet1',
            'type': 'Microsoft.Network/virtualNetworks/subnets',
            'vnetId': '/subscriptions/12345/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/vnet1',
            'resourceGroup': 'rg1',
            'subscriptionId': '12345'
        },
        {
            'id': '/subscriptions/12345/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm1',
            'name': 'vm1',
            'type': 'Microsoft.Compute/virtualMachines',
            'resourceGroup': 'rg1',
            'subscriptionId': '12345',
            'properties': {
                'subnet': {
                    'id': '/subscriptions/12345/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/vnet1/subnets/subnet1'
                }
            }
        }
    ]
    
    print("Generando diagrama...")
    content = generate_drawio_file(
        test_items, 
        [],
        embed_data=False,
        include_ids=None,
        diagram_mode='network'
    )
    
    with open('./fixtures/test-simple-network.drawio', 'w') as f:
        f.write(content)
    
    print("Archivo generado: ./fixtures/test-simple-network.drawio")
    print("Tamaño:", len(content), "caracteres")
    
except Exception as e:
    print("Error:", str(e))
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad con el CLI principal
"""

import json
import os
import sys

def create_test_data():
    """Crea datos de prueba en formato JSON compatible con el CLI"""
    
    test_data = {
        "items": [
            # Management Group
            {
                "id": "/providers/Microsoft.Management/managementGroups/test-mg",
                "type": "Microsoft.Management/managementGroups",
                "name": "test-mg",
                "properties": {
                    "displayName": "Test Management Group",
                    "tenantId": "test-tenant"
                }
            },
            
            # Subscription
            {
                "id": "/subscriptions/test-sub-001",
                "type": "Microsoft.Resources/subscriptions",
                "name": "test-sub-001",
                "properties": {
                    "subscriptionId": "test-sub-001",
                    "displayName": "Test Subscription"
                }
            },
            
            # Resource Group
            {
                "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network",
                "type": "Microsoft.Resources/subscriptions/resourceGroups",
                "name": "test-rg-network",
                "location": "eastus",
                "properties": {}
            },
            
            # VNet
            {
                "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/virtualNetworks/test-vnet",
                "type": "Microsoft.Network/virtualNetworks",
                "name": "test-vnet",
                "location": "eastus",
                "properties": {
                    "addressSpace": {"addressPrefixes": ["10.0.0.0/16"]},
                    "subnets": []
                }
            },
            
            # Subnet 1
            {
                "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet-web",
                "type": "Microsoft.Network/virtualNetworks/subnets",
                "name": "subnet-web",
                "properties": {
                    "addressPrefix": "10.0.1.0/24",
                    "networkSecurityGroup": {
                        "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/networkSecurityGroups/nsg-multi"
                    },
                    "routeTable": {
                        "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/routeTables/rt-multi"
                    }
                }
            },
            
            # Subnet 2
            {
                "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet-app",
                "type": "Microsoft.Network/virtualNetworks/subnets",
                "name": "subnet-app",
                "properties": {
                    "addressPrefix": "10.0.2.0/24",
                    "networkSecurityGroup": {
                        "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/networkSecurityGroups/nsg-multi"
                    },
                    "routeTable": {
                        "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/routeTables/rt-multi"
                    }
                }
            },
            
            # NSG Multi-subnet
            {
                "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/networkSecurityGroups/nsg-multi",
                "type": "Microsoft.Network/networkSecurityGroups",
                "name": "nsg-multi",
                "location": "eastus",
                "properties": {
                    "securityRules": [],
                    "subnets": [
                        {
                            "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet-web"
                        },
                        {
                            "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet-app"
                        }
                    ]
                }
            },
            
            # Route Table Multi-subnet
            {
                "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/routeTables/rt-multi",
                "type": "Microsoft.Network/routeTables",
                "name": "rt-multi",
                "location": "eastus",
                "properties": {
                    "routes": [],
                    "subnets": [
                        {
                            "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet-web"
                        },
                        {
                            "id": "/subscriptions/test-sub-001/resourceGroups/test-rg-network/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet-app"
                        }
                    ]
                }
            }
        ],
        "dependencies": []
    }
    
    return test_data

def main():
    print("🧪 Creando datos de prueba para NSG y Route Table multi-subnet...")
    
    # Crear directorio data si no existe
    os.makedirs("data", exist_ok=True)
    
    # Crear datos de prueba
    test_data = create_test_data()
    
    # Guardar en archivo JSON
    test_file = "data/test_multi_subnet.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Datos de prueba guardados en: {test_file}")
    print(f"📊 Recursos creados: {len(test_data['items'])}")
    print("   - 1 NSG asociado a 2 subnets")
    print("   - 1 Route Table asociado a 2 subnets")
    
    print("\n🚀 Para probar con el CLI principal:")
    print(f"   python src/cli.py --from-file {test_file} --diagram-mode network --output data/test_multi_subnet.drawio")
    
    print("\n📋 Verificaciones esperadas:")
    print("   1. NSG original en Resource Group")
    print("   2. NSG (asignación) en subnet-web")
    print("   3. NSG (asignación) en subnet-app")
    print("   4. Route Table original en Resource Group")
    print("   5. Route Table (asignación) en subnet-web")
    print("   6. Route Table (asignación) en subnet-app")

if __name__ == "__main__":
    main()

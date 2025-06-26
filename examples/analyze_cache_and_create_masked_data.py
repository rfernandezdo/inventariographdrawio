#!/usr/bin/env python3
"""
analyze_cache_and_create_masked_data.py

Analiza la cache local de Azure y crea datos enmascarados realistas para mejorar los tests.
"""

import json
import re
import uuid
from collections import defaultdict
from datetime import datetime


def analyze_cache_structure(cache_file):
    """Analiza la estructura de la cache para entender los patrones."""
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    
    items = cache_data.get('data', [])
    
    # Análisis estadístico
    stats = {
        'total_items': len(items),
        'types': defaultdict(int),
        'locations': defaultdict(int),
        'naming_patterns': defaultdict(list),
        'hierarchies': defaultdict(list)
    }
    
    for item in items:
        item_type = item.get('type', '').lower()
        stats['types'][item_type] += 1
        
        location = item.get('location', '')
        if location:
            stats['locations'][location] += 1
        
        # Analizar patrones de nombres
        name = item.get('name', '')
        if name:
            # Extraer patrones como prefijos-sufijos
            parts = re.split(r'[-_]', name)
            if len(parts) > 1:
                pattern = f"{parts[0]}-*-{parts[-1]}" if len(parts) > 2 else f"{parts[0]}-*"
                stats['naming_patterns'][item_type].append(pattern)
        
        # Analizar jerarquías
        item_id = item.get('id', '')
        if 'resourceGroups' in item_id:
            parts = item_id.split('/')
            if len(parts) >= 6:
                rg_name = parts[4]
                stats['hierarchies']['resource_groups'].append(rg_name)
    
    return stats


def create_masked_realistic_data(stats):
    """Crea datos enmascarados basados en los patrones reales."""
    
    # IDs enmascarados pero realistas
    fake_tenant_id = "12345678-1234-1234-1234-123456789012"
    fake_subscription_id = "abcdef12-3456-7890-abcd-ef1234567890"
    
    masked_data = {
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "source": "masked_real_patterns",
            "total_items": 0,
            "total_dependencies": 0
        },
        "items": [],
        "dependencies": []
    }
    
    # 1. Management Groups con jerarquía realista
    mg_items = [
        {
            "id": f"/providers/Microsoft.Management/managementGroups/contoso-root",
            "type": "microsoft.management/managementgroups",
            "name": "contoso-root",
            "displayName": "Contoso Root",
            "properties": {
                "tenantId": fake_tenant_id,
                "displayName": "Contoso Root",
                "details": {
                    "managementGroupAncestorsChain": [
                        {
                            "displayName": "Tenant Root Group",
                            "name": fake_tenant_id
                        }
                    ],
                    "parent": {
                        "displayName": "Tenant Root Group",
                        "id": f"/providers/Microsoft.Management/managementGroups/{fake_tenant_id}",
                        "name": fake_tenant_id
                    }
                }
            }
        },
        {
            "id": f"/providers/Microsoft.Management/managementGroups/contoso-platform",
            "type": "microsoft.management/managementgroups",
            "name": "contoso-platform",
            "displayName": "Platform",
            "properties": {
                "tenantId": fake_tenant_id,
                "displayName": "Platform",
                "details": {
                    "managementGroupAncestorsChain": [
                        {
                            "displayName": "Contoso Root",
                            "name": "contoso-root"
                        },
                        {
                            "displayName": "Tenant Root Group",
                            "name": fake_tenant_id
                        }
                    ],
                    "parent": {
                        "displayName": "Contoso Root",
                        "id": f"/providers/Microsoft.Management/managementGroups/contoso-root",
                        "name": "contoso-root"
                    }
                }
            }
        },
        {
            "id": f"/providers/Microsoft.Management/managementGroups/contoso-connectivity",
            "type": "microsoft.management/managementgroups",
            "name": "contoso-connectivity",
            "displayName": "Connectivity",
            "properties": {
                "tenantId": fake_tenant_id,
                "displayName": "Connectivity",
                "details": {
                    "managementGroupAncestorsChain": [
                        {
                            "displayName": "Platform",
                            "name": "contoso-platform"
                        },
                        {
                            "displayName": "Contoso Root",
                            "name": "contoso-root"
                        },
                        {
                            "displayName": "Tenant Root Group",
                            "name": fake_tenant_id
                        }
                    ],
                    "parent": {
                        "displayName": "Platform",
                        "id": f"/providers/Microsoft.Management/managementGroups/contoso-platform",
                        "name": "contoso-platform"
                    }
                }
            }
        }
    ]
    
    # 2. Suscripción
    subscription_item = {
        "id": f"/subscriptions/{fake_subscription_id}",
        "type": "microsoft.resources/subscriptions",
        "name": "contoso-prod-001",
        "subscriptionId": fake_subscription_id,
        "properties": {
            "managedByTenants": [],
            "managementGroupAncestorsChain": [
                {
                    "displayName": "Connectivity",
                    "name": "contoso-connectivity"
                },
                {
                    "displayName": "Platform", 
                    "name": "contoso-platform"
                },
                {
                    "displayName": "Contoso Root",
                    "name": "contoso-root"
                },
                {
                    "displayName": "Tenant Root Group",
                    "name": fake_tenant_id
                }
            ],
            "state": "Enabled",
            "subscriptionPolicies": {
                "locationPlacementId": "Public_2014-09-01",
                "quotaId": "PayAsYouGo_2014-09-01",
                "spendingLimit": "Off"
            }
        },
        "tenantId": fake_tenant_id
    }
    
    # 3. Resource Groups con patrones realistas
    rg_items = [
        {
            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-network-prd-we-001",
            "type": "microsoft.resources/subscriptions/resourcegroups",
            "name": "rg-network-prd-we-001",
            "location": "westeurope",
            "resourceGroup": "rg-network-prd-we-001",
            "subscriptionId": fake_subscription_id,
            "properties": {
                "provisioningState": "Succeeded"
            },
            "tags": {
                "environment": "production",
                "project": "networking"
            }
        },
        {
            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-compute-prd-we-001",
            "type": "microsoft.resources/subscriptions/resourcegroups",
            "name": "rg-compute-prd-we-001",
            "location": "westeurope",
            "resourceGroup": "rg-compute-prd-we-001",
            "subscriptionId": fake_subscription_id,
            "properties": {
                "provisioningState": "Succeeded"
            },
            "tags": {
                "environment": "production",
                "project": "compute"
            }
        }
    ]
    
    # 4. Recursos de red con estructura realista
    network_items = [
        {
            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-network-prd-we-001/providers/Microsoft.Network/virtualNetworks/vnet-hub-prd-we-001",
            "type": "microsoft.network/virtualnetworks",
            "name": "vnet-hub-prd-we-001",
            "location": "westeurope",
            "resourceGroup": "rg-network-prd-we-001",
            "subscriptionId": fake_subscription_id,
            "properties": {
                "addressSpace": {
                    "addressPrefixes": ["10.0.0.0/16"]
                },
                "enableDdosProtection": False,
                "provisioningState": "Succeeded"
            },
            "tags": {
                "environment": "production",
                "type": "hub"
            }
        },
        {
            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-network-prd-we-001/providers/Microsoft.Network/virtualNetworks/vnet-hub-prd-we-001/subnets/snet-gateway-prd-we-001",
            "type": "microsoft.network/virtualnetworks/subnets",
            "name": "snet-gateway-prd-we-001",
            "resourceGroup": "rg-network-prd-we-001",
            "subscriptionId": fake_subscription_id,
            "vnetId": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-network-prd-we-001/providers/Microsoft.Network/virtualNetworks/vnet-hub-prd-we-001",
            "properties": {
                "addressPrefix": "10.0.1.0/24",
                "provisioningState": "Succeeded"
            }
        },
        {
            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-network-prd-we-001/providers/Microsoft.Network/virtualNetworks/vnet-hub-prd-we-001/subnets/snet-compute-prd-we-001",
            "type": "microsoft.network/virtualnetworks/subnets",
            "name": "snet-compute-prd-we-001",
            "resourceGroup": "rg-network-prd-we-001",
            "subscriptionId": fake_subscription_id,
            "vnetId": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-network-prd-we-001/providers/Microsoft.Network/virtualNetworks/vnet-hub-prd-we-001",
            "properties": {
                "addressPrefix": "10.0.2.0/24",
                "provisioningState": "Succeeded"
            }
        },
        {
            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-network-prd-we-001/providers/Microsoft.Network/publicIPAddresses/pip-gateway-prd-we-001",
            "type": "microsoft.network/publicipaddresses",
            "name": "pip-gateway-prd-we-001",
            "location": "westeurope",
            "resourceGroup": "rg-network-prd-we-001",
            "subscriptionId": fake_subscription_id,
            "properties": {
                "publicIPAllocationMethod": "Static",
                "publicIPAddressVersion": "IPv4",
                "provisioningState": "Succeeded"
            }
        },
        {
            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-network-prd-we-001/providers/Microsoft.Network/networkSecurityGroups/nsg-compute-prd-we-001",
            "type": "microsoft.network/networksecuritygroups",
            "name": "nsg-compute-prd-we-001",
            "location": "westeurope",
            "resourceGroup": "rg-network-prd-we-001",
            "subscriptionId": fake_subscription_id,
            "properties": {
                "provisioningState": "Succeeded",
                "securityRules": []
            }
        },
        {
            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-network-prd-we-001/providers/Microsoft.Network/applicationGateways/agw-web-prd-we-001",
            "type": "microsoft.network/applicationgateways",
            "name": "agw-web-prd-we-001",
            "location": "westeurope",
            "resourceGroup": "rg-network-prd-we-001",
            "subscriptionId": fake_subscription_id,
            "properties": {
                "provisioningState": "Succeeded",
                "sku": {
                    "name": "Standard_v2",
                    "tier": "Standard_v2"
                }
            }
        }
    ]
    
    # 5. Recursos de cómputo
    compute_items = [
        {
            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-compute-prd-we-001/providers/Microsoft.Compute/virtualMachines/vm-web-prd-we-001",
            "type": "microsoft.compute/virtualmachines",
            "name": "vm-web-prd-we-001",
            "location": "westeurope",
            "resourceGroup": "rg-compute-prd-we-001",
            "subscriptionId": fake_subscription_id,
            "properties": {
                "hardwareProfile": {
                    "vmSize": "Standard_B2s"
                },
                "storageProfile": {
                    "osDisk": {
                        "osType": "Linux"
                    }
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-compute-prd-we-001/providers/Microsoft.Network/networkInterfaces/nic-vm-web-prd-we-001"
                        }
                    ]
                },
                "provisioningState": "Succeeded"
            }
        },
        {
            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-compute-prd-we-001/providers/Microsoft.Web/sites/app-web-prd-we-001",
            "type": "microsoft.web/sites",
            "name": "app-web-prd-we-001",
            "location": "westeurope",
            "resourceGroup": "rg-compute-prd-we-001",
            "subscriptionId": fake_subscription_id,
            "properties": {
                "state": "Running",
                "serverFarmId": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-compute-prd-we-001/providers/Microsoft.Web/serverfarms/plan-web-prd-we-001"
            }
        }
    ]
    
    # 6. Recursos de almacenamiento
    storage_items = [
        {
            "id": f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-compute-prd-we-001/providers/Microsoft.Storage/storageAccounts/stcontosoprdwe001",
            "type": "microsoft.storage/storageaccounts",
            "name": "stcontosoprdwe001",
            "location": "westeurope",
            "resourceGroup": "rg-compute-prd-we-001",
            "subscriptionId": fake_subscription_id,
            "properties": {
                "primaryLocation": "westeurope",
                "provisioningState": "Succeeded",
                "accountType": "Standard_LRS"
            }
        }
    ]
    
    # Combinar todos los items
    all_items = mg_items + [subscription_item] + rg_items + network_items + compute_items + storage_items
    
    # Crear dependencias jerárquicas
    dependencies = []
    
    # MG dependencies
    dependencies.append([f"/providers/Microsoft.Management/managementGroups/{fake_tenant_id}", "/providers/Microsoft.Management/managementGroups/contoso-root"])
    dependencies.append(["/providers/Microsoft.Management/managementGroups/contoso-root", "/providers/Microsoft.Management/managementGroups/contoso-platform"])
    dependencies.append(["/providers/Microsoft.Management/managementGroups/contoso-platform", "/providers/Microsoft.Management/managementGroups/contoso-connectivity"])
    
    # Subscription dependencies
    dependencies.append(["/providers/Microsoft.Management/managementGroups/contoso-connectivity", f"/subscriptions/{fake_subscription_id}"])
    
    # RG dependencies
    for rg_item in rg_items:
        dependencies.append([f"/subscriptions/{fake_subscription_id}", rg_item["id"]])
    
    # Resource dependencies
    for item in network_items + compute_items + storage_items:
        rg_id = f"/subscriptions/{fake_subscription_id}/resourceGroups/{item['resourceGroup']}"
        dependencies.append([rg_id, item["id"]])
    
    # VNet -> Subnet dependencies
    vnet_id = f"/subscriptions/{fake_subscription_id}/resourceGroups/rg-network-prd-we-001/providers/Microsoft.Network/virtualNetworks/vnet-hub-prd-we-001"
    for item in network_items:
        if item["type"] == "microsoft.network/virtualnetworks/subnets":
            dependencies.append([vnet_id, item["id"]])
    
    masked_data["items"] = all_items
    masked_data["dependencies"] = dependencies
    masked_data["metadata"]["total_items"] = len(all_items)
    masked_data["metadata"]["total_dependencies"] = len(dependencies)
    
    return masked_data


def main():
    print("🔍 Analizando cache local de Azure...")
    
    cache_file = '.azure_cache/final_inventory_20250626_23.json'
    
    if not os.path.exists(cache_file):
        print(f"❌ No se encontró el archivo de cache: {cache_file}")
        return
    
    # Analizar estructura
    stats = analyze_cache_structure(cache_file)
    
    print(f"📊 Análisis de la cache:")
    print(f"   Total de recursos: {stats['total_items']}")
    print(f"   Tipos encontrados: {len(stats['types'])}")
    print(f"   Locations: {list(stats['locations'].keys())}")
    
    print(f"\n🔝 Tipos más comunes:")
    for resource_type, count in sorted(stats['types'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {resource_type}: {count}")
    
    # Crear datos enmascarados
    print(f"\n🎭 Creando datos enmascarados realistas...")
    masked_data = create_masked_realistic_data(stats)
    
    # Guardar datos enmascarados
    output_file = 'masked_realistic_inventory.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(masked_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Datos enmascarados guardados en: {output_file}")
    print(f"   📊 {masked_data['metadata']['total_items']} recursos")
    print(f"   🔗 {masked_data['metadata']['total_dependencies']} dependencias")
    print(f"\n💡 Uso: python3 test_with_real_data.py --input {output_file} --mode network")


if __name__ == '__main__':
    import os
    main()

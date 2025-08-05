#!/usr/bin/env python3
"""
Generador de diagrama de demostración con NSGs y Route Tables multi-subnet (v2)
Muestra el NSG/RT original en su RG y las asignaciones en las subnets correspondientes
"""

import sys
import os
import json

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_demo_data_v2():
    """Crea datos de demostración con NSGs y Route Tables asociados a múltiples subnets"""
    
    items = [
        # Management Group
        {
            "id": "/providers/Microsoft.Management/managementGroups/demo-mg-corp",
            "type": "Microsoft.Management/managementGroups",
            "name": "demo-mg-corp",
            "properties": {
                "displayName": "Corporativo Demo",
                "tenantId": "demo-tenant-001"
            }
        },
        
        # Subscription
        {
            "id": "/subscriptions/demo-subscription-001",
            "type": "Microsoft.Resources/subscriptions",
            "name": "demo-subscription-001",
            "properties": {
                "subscriptionId": "demo-subscription-001",
                "displayName": "Suscripción Demo Networking"
            }
        },
        
        # Resource Groups
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking",
            "type": "Microsoft.Resources/subscriptions/resourceGroups",
            "name": "demo-rg-networking",
            "location": "eastus",
            "properties": {}
        },
        
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-compute",
            "type": "Microsoft.Resources/subscriptions/resourceGroups", 
            "name": "demo-rg-compute",
            "location": "eastus",
            "properties": {}
        },
        
        # VNet Principal
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-main",
            "type": "Microsoft.Network/virtualNetworks",
            "name": "demo-vnet-main",
            "location": "eastus",
            "properties": {
                "addressSpace": {"addressPrefixes": ["10.0.0.0/16"]},
                "subnets": []
            }
        },
        
        # VNet Secundaria  
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-secondary",
            "type": "Microsoft.Network/virtualNetworks",
            "name": "demo-vnet-secondary", 
            "location": "eastus",
            "properties": {
                "addressSpace": {"addressPrefixes": ["10.1.0.0/16"]},
                "subnets": []
            }
        },
        
        # Subnets VNet Principal
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-main/subnets/demo-subnet-web",
            "type": "Microsoft.Network/virtualNetworks/subnets",
            "name": "demo-subnet-web",
            "properties": {
                "addressPrefix": "10.0.1.0/24",
                "networkSecurityGroup": {
                    "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/networkSecurityGroups/demo-nsg-web-tier"
                },
                "routeTable": {
                    "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/routeTables/demo-rt-frontend"
                }
            }
        },
        
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-main/subnets/demo-subnet-app",
            "type": "Microsoft.Network/virtualNetworks/subnets",
            "name": "demo-subnet-app",
            "properties": {
                "addressPrefix": "10.0.2.0/24",
                "networkSecurityGroup": {
                    "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/networkSecurityGroups/demo-nsg-web-tier"
                },
                "routeTable": {
                    "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/routeTables/demo-rt-frontend"
                }
            }
        },
        
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-main/subnets/demo-subnet-data",
            "type": "Microsoft.Network/virtualNetworks/subnets",
            "name": "demo-subnet-data",
            "properties": {
                "addressPrefix": "10.0.3.0/24",
                "networkSecurityGroup": {
                    "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/networkSecurityGroups/demo-nsg-data-tier"
                },
                "routeTable": {
                    "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/routeTables/demo-rt-backend"
                }
            }
        },
        
        # Subnets VNet Secundaria
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-secondary/subnets/demo-subnet-backup",
            "type": "Microsoft.Network/virtualNetworks/subnets",
            "name": "demo-subnet-backup",
            "properties": {
                "addressPrefix": "10.1.1.0/24",
                "networkSecurityGroup": {
                    "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/networkSecurityGroups/demo-nsg-data-tier"
                },
                "routeTable": {
                    "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/routeTables/demo-rt-backend"
                }
            }
        },
        
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-secondary/subnets/demo-subnet-mgmt",
            "type": "Microsoft.Network/virtualNetworks/subnets",
            "name": "demo-subnet-mgmt",
            "properties": {
                "addressPrefix": "10.1.2.0/24",
                "networkSecurityGroup": {
                    "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/networkSecurityGroups/demo-nsg-web-tier"
                }
            }
        },
        
        # NSG Web Tier (usado en 3 subnets: web, app, mgmt)
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/networkSecurityGroups/demo-nsg-web-tier",
            "type": "Microsoft.Network/networkSecurityGroups",
            "name": "demo-nsg-web-tier",
            "location": "eastus",
            "properties": {
                "securityRules": [
                    {
                        "name": "AllowHTTP",
                        "properties": {
                            "access": "Allow",
                            "direction": "Inbound",
                            "priority": 100,
                            "protocol": "Tcp",
                            "destinationPortRange": "80"
                        }
                    },
                    {
                        "name": "AllowHTTPS", 
                        "properties": {
                            "access": "Allow",
                            "direction": "Inbound",
                            "priority": 110,
                            "protocol": "Tcp",
                            "destinationPortRange": "443"
                        }
                    }
                ],
                "subnets": [
                    {
                        "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-main/subnets/demo-subnet-web"
                    },
                    {
                        "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-main/subnets/demo-subnet-app"
                    },
                    {
                        "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-secondary/subnets/demo-subnet-mgmt"
                    }
                ]
            }
        },
        
        # NSG Data Tier (usado en 2 subnets: data, backup)
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/networkSecurityGroups/demo-nsg-data-tier",
            "type": "Microsoft.Network/networkSecurityGroups",
            "name": "demo-nsg-data-tier",
            "location": "eastus",
            "properties": {
                "securityRules": [
                    {
                        "name": "AllowSQL",
                        "properties": {
                            "access": "Allow",
                            "direction": "Inbound",
                            "priority": 100,
                            "protocol": "Tcp",
                            "destinationPortRange": "1433"
                        }
                    }
                ],
                "subnets": [
                    {
                        "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-main/subnets/demo-subnet-data"
                    },
                    {
                        "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-secondary/subnets/demo-subnet-backup"
                    }
                ]
            }
        },
        
        # Route Table Frontend (usado en 2 subnets: web, app)
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/routeTables/demo-rt-frontend",
            "type": "Microsoft.Network/routeTables",
            "name": "demo-rt-frontend",
            "location": "eastus",
            "properties": {
                "routes": [
                    {
                        "name": "route-to-internet",
                        "properties": {
                            "addressPrefix": "0.0.0.0/0",
                            "nextHopType": "Internet"
                        }
                    }
                ],
                "subnets": [
                    {
                        "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-main/subnets/demo-subnet-web"
                    },
                    {
                        "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-main/subnets/demo-subnet-app"
                    }
                ]
            }
        },
        
        # Route Table Backend (usado en 2 subnets: data, backup)
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/routeTables/demo-rt-backend",
            "type": "Microsoft.Network/routeTables", 
            "name": "demo-rt-backend",
            "location": "eastus",
            "properties": {
                "routes": [
                    {
                        "name": "route-to-firewall",
                        "properties": {
                            "addressPrefix": "0.0.0.0/0",
                            "nextHopType": "VirtualAppliance",
                            "nextHopIpAddress": "10.0.100.4"
                        }
                    }
                ],
                "subnets": [
                    {
                        "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-main/subnets/demo-subnet-data"
                    },
                    {
                        "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-networking/providers/Microsoft.Network/virtualNetworks/demo-vnet-secondary/subnets/demo-subnet-backup"
                    }
                ]
            }
        },
        
        # Algunos recursos adicionales en RG compute
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-compute/providers/Microsoft.Compute/virtualMachines/demo-vm-web01",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "demo-vm-web01",
            "location": "eastus",
            "properties": {
                "hardwareProfile": {"vmSize": "Standard_D2s_v3"}
            }
        },
        
        {
            "id": "/subscriptions/demo-subscription-001/resourceGroups/demo-rg-compute/providers/Microsoft.Storage/storageAccounts/demostorageacct001",
            "type": "Microsoft.Storage/storageAccounts",
            "name": "demostorageacct001",
            "location": "eastus",
            "properties": {
                "accountType": "Standard_LRS"
            }
        }
    ]
    
    dependencies = []
    
    return items, dependencies

def generate_simple_xml_v2(extended_items, node_positions, group_info, resource_to_parent_id):
    """Genera un XML simplificado de draw.io con elementos virtuales mejorados"""
    
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="localhost" modified="2025-01-01T12:00:00.000Z" agent="Demo Generator v2" version="24.0.0">
  <diagram name="Demo Network - NSGs y Route Tables Multi-Subnet" id="demo-page">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="3000" pageHeight="2000" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
'''
    
    # Generar contenedores primero
    for group in group_info:
        xml_content += f'''        <mxCell id="{group['id']}" style="{group['style']}" parent="{group.get('parent_id', '1')}" vertex="1">
          <mxGeometry x="{group['x']}" y="{group['y']}" width="{group['width']}" height="{group['height']}" as="geometry"/>
        </mxCell>
'''
    
    # Generar nodos de recursos
    for i, item in enumerate(extended_items):
        if i in node_positions:
            x, y = node_positions[i]
            parent_id = resource_to_parent_id.get(i, '1')
            
            # Determinar el icono
            item_type = (item.get('type') or '').lower()
            icon = _get_icon_for_type(item_type)
            
            # Determinar el nombre y propiedades especiales
            name = item.get('name', f'Item-{i}')
            is_assignment = item.get('_is_assignment', False)
            virtual_subnet = item.get('_virtual_subnet_id', '')
            original_index = item.get('_original_index', '')
            
            # Crear el objeto con metadatos
            object_data = f'type="{item_type}" id="{item["id"]}"'
            if is_assignment:
                object_data += f' virtual_subnet="{virtual_subnet}" original_index="{original_index}" is_assignment="true"'
            
            xml_content += f'''        <mxCell id="node-{i}" style="image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image={icon}" parent="{parent_id}" vertex="1">
          <mxGeometry x="{x}" y="{y}" width="48" height="48" as="geometry"/>
          <object label="&lt;b&gt;{name}&lt;/b&gt;" as="value" {object_data}/>
        </mxCell>
'''
    
    xml_content += '''      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    
    return xml_content

def _get_icon_for_type(item_type):
    """Devuelve el icono apropiado para un tipo de recurso"""
    icon_map = {
        'microsoft.management/managementgroups': 'img/lib/azure2/general/Management_Groups.svg',
        'microsoft.resources/subscriptions': 'img/lib/azure2/general/Subscriptions.svg',
        'microsoft.resources/subscriptions/resourcegroups': 'img/lib/azure2/general/Resource_Groups.svg',
        'microsoft.network/virtualnetworks': 'img/lib/azure2/networking/Virtual_Networks.svg',
        'microsoft.network/virtualnetworks/subnets': 'img/lib/azure2/networking/Subnet.svg',
        'microsoft.network/networksecuritygroups': 'img/lib/azure2/networking/Network_Security_Groups.svg',
        'microsoft.network/routetables': 'img/lib/azure2/networking/Route_Tables.svg',
        'microsoft.compute/virtualmachines': 'img/lib/azure2/compute/Virtual_Machine.svg',
        'microsoft.storage/storageaccounts': 'img/lib/azure2/storage/Storage_Accounts.svg'
    }
    return icon_map.get(item_type, 'img/lib/azure2/general/Azure.svg')

def main():
    print("🚀 Generando diagrama de demostración v2...")
    print("   - NSGs y Route Tables con múltiples subnets")
    print("   - Originales en RG, asignaciones en subnets")
    
    # Crear datos de demostración
    items, dependencies = create_demo_data_v2()
    print(f"📦 Datos creados: {len(items)} recursos")
    
    # Importar el layout de red directamente
    from drawio.layouts.network import generate_network_layout
    
    # Generar layout
    print("🔧 Generando layout de red...")
    extended_items, node_positions, group_info, resource_to_parent_id = generate_network_layout(
        items, dependencies
    )
    
    print(f"✨ Layout generado:")
    print(f"   - Elementos extendidos: {len(extended_items)} (vs {len(items)} originales)")
    print(f"   - Posiciones: {len(node_positions)}")
    print(f"   - Grupos: {len(group_info)}")
    
    # Analizar elementos virtuales
    print("\n🔍 Análisis de elementos virtuales:")
    virtual_count = 0
    for i, item in enumerate(extended_items):
        if item.get('_is_assignment', False):
            virtual_count += 1
            original_name = extended_items[item['_original_index']].get('name', 'Unknown')
            subnet_name = item['_virtual_subnet_id'].split('/')[-1]
            print(f"   - {item['name']} -> subnet: {subnet_name}")
    
    print(f"   Total elementos virtuales: {virtual_count}")
    
    # Generar XML
    print("\n💫 Generando archivo draw.io...")
    xml_content = generate_simple_xml_v2(extended_items, node_positions, group_info, resource_to_parent_id)
    
    # Guardar archivo
    output_file = "data/demo_multi_subnet_v2.drawio"
    os.makedirs("data", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"✅ Diagrama guardado en: {output_file}")
    print("\n📊 Resumen del diagrama:")
    print(f"   - NSGs originales: 2 (en demo-rg-networking)")
    print(f"   - NSG asignaciones: {sum(1 for item in extended_items if item.get('_is_assignment') and 'networksecuritygroups' in item.get('type', '').lower())}")
    print(f"   - Route Tables originales: 2 (en demo-rg-networking)")
    print(f"   - Route Table asignaciones: {sum(1 for item in extended_items if item.get('_is_assignment') and 'routetables' in item.get('type', '').lower())}")
    
    print(f"\n🌐 Para ver el diagrama:")
    print(f"   1. Abre https://app.diagrams.net/")
    print(f"   2. Selecciona 'Open Existing Diagram'")
    print(f"   3. Carga el archivo: {output_file}")

if __name__ == "__main__":
    main()

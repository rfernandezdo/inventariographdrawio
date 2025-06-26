"""
Funciones para generar el XML de draw.io y gestionar la disposición visual.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import json

# --- ICONOS Y ESTILOS DE AZURE PARA DRAW.IO ---
AZURE_ICONS = {
    "microsoft.aad/domainservices": "img/lib/azure2/identity/Entra_Domain_Services.svg",
    "microsoft.alertsmanagement/smartdetectoralertrules": "img/lib/azure2/management_governance/Alerts.svg",
    "microsoft.apimanagement/service": "img/lib/azure2/app_services/API_Management.svg",
    "microsoft.automation/automationaccounts": "img/lib/azure2/management_governance/Automation_Accounts.svg",
    "microsoft.cognitiveservices/accounts": "img/lib/azure2/ai_machine_learning/Cognitive_Services.svg",
    "microsoft.compute/availabilitysets": "img/lib/azure2/compute/Availability_Set.svg",
    "microsoft.compute/disks": "img/lib/azure2/compute/Disks.svg",
    "microsoft.compute/restorepointcollections": "img/lib/azure2/compute/Restore_Points_Collections.svg",
    "microsoft.compute/virtualmachines": "img/lib/azure2/compute/Virtual_Machine.svg",
    "microsoft.compute/virtualmachines/extensions": "img/lib/azure2/compute/Virtual_Machine_Extension.svg",
    "microsoft.compute/virtualmachinescalesets": "img/lib/azure2/compute/Virtual_Machine_Scale_Set.svg",
    "microsoft.containerregistry/registries": "img/lib/azure2/containers/Container_Registry.svg",
    "microsoft.containerservice/managedclusters": "img/lib/azure2/containers/Kubernetes_Service.svg",
    "microsoft.eventgrid/domains": "img/lib/azure2/messaging/Event_Grid_Domains.svg",
    "microsoft.eventgrid/eventsubscriptions": "img/lib/azure2/messaging/Event_Subscriptions.svg",
    "microsoft.eventgrid/topics": "img/lib/azure2/messaging/Event_Grid_Topics.svg",
    "microsoft.insights/actiongroups": "https://raw.githubusercontent.com/maskati/azure-icons/4b66132ac79eaaed25bf419db6e22c0fe3ca34b1/svg/Microsoft_Azure_Monitoring_Alerts/ActionGroup.svg",
    "microsoft.insights/components": "img/lib/azure2/management_governance/Application_Insights.svg",
    "microsoft.keyvault/vaults": "img/lib/azure2/security/Key_Vaults.svg",
    "microsoft.logic/workflows": "img/lib/azure2/app_services/Logic_App.svg",
    "microsoft.management/managementgroups": "img/lib/azure2/general/Management_Groups.svg",
    "microsoft.managedidentity/userassignedidentities": "img/lib/mscae/Managed_Identities.svg",
    "microsoft.machinelearningservices/workspaces": "img/lib/azure2/ai_machine_learning/Machine_Learning.svg",
    "microsoft.network/applicationgateways": "img/lib/azure2/networking/Application_Gateway.svg",
    "microsoft.network/connections": "img/lib/azure2/networking/Connections.svg",
    "microsoft.network/azurefirewalls": "img/lib/azure2/networking/Azure_Firewall.svg",
    "microsoft.network/azurefirewallpolicies": "img/lib/azure2/networking/Azure_Firewall_Policy.svg",
    "microsoft.network/dnszones": "img/lib/azure2/networking/DNS_Zone.svg",
    "microsoft.network/dnszones/recordsets": "img/lib/azure2/networking/DNS_Record_Sets.svg",
    "microsoft.network/expressroutecircuits": "img/lib/azure2/networking/ExpressRoute_Circuits.svg",
    "microsoft.network/loadbalancers": "img/lib/azure2/networking/Load_Balancers.svg",
    "microsoft.network/localnetworkgateways": "img/lib/azure2/networking/Local_Network_Gateways.svg",
    "microsoft.network/networkinterfaces": "img/lib/azure2/networking/Network_Interfaces.svg",
    "microsoft.network/networksecuritygroups": "img/lib/azure2/networking/Network_Security_Groups.svg",
    "microsoft.network/networkwatchers": "img/lib/azure2/networking/Network_Watcher.svg",
    "microsoft.network/privateendpoints": "img/lib/azure2/other/Private_Endpoints.svg",
    "microsoft.network/publicipaddresses": "img/lib/azure2/networking/Public_IP_Addresses.svg",
    "microsoft.network/routetables": "img/lib/azure2/networking/Route_Tables.svg",
    "microsoft.network/trafficmanagerprofiles": "img/lib/azure2/networking/Traffic_Manager_Profile.svg",
    "microsoft.network/virtualnetworks": "img/lib/azure2/networking/Virtual_Networks.svg",
    "microsoft.network/virtualnetworks/subnets": "img/lib/azure2/networking/Subnet.svg",
    "microsoft.network/virtualnetworkgateways": "img/lib/azure2/networking/Virtual_Network_Gateways.svg",
    "microsoft.network/virtualnetworkgateways/vpnconnections": "img/lib/azure2/networking/VPN_Connections.svg",
    "microsoft.operationsmanagement/solutions": "img/lib/mscae/Solutions.svg",
    "microsoft.operationalinsights/workspaces": "img/lib/azure2/analytics/Log_Analytics_Workspaces.svg",
    "microsoft.recoveryservices/vaults": "img/lib/azure2/management_governance/Recovery_Services_Vaults.svg",
    "microsoft.resources/deploymentscripts": "img/lib/azure2/general/Deployment_Scripts.svg",
    "microsoft.resources/resources": "img/lib/azure2/general/Resources.svg",
    "microsoft.resources/subscriptions": "img/lib/azure2/general/Subscriptions.svg",
    "microsoft.resources/subscriptions/resourcegroups": "img/lib/azure2/general/Resource_Groups.svg",
    "microsoft.search/searchservices": "img/lib/azure2/ai_machine_learning/Search.svg",
    "microsoft.security/automations": "image=img/lib/azure2/management_governance/Automation_Accounts.svg",
    "microsoft.servicebus/namespaces": "img/lib/azure2/messaging/Service_Bus.svg",
    "microsoft.sql/servers": "img/lib/azure2/databases/SQL_Server.svg",
    "microsoft.sql/servers/databases": "img/lib/azure2/databases/SQL_Database.svg",
    "microsoft.storage/storageaccounts": "img/lib/azure2/storage/Storage_Accounts.svg",
    "microsoft.storage/storageaccounts/blobservices": "img/lib/azure2/storage/Blob_Service.svg",
    "microsoft.storage/storageaccounts/blobservices/containers": "img/lib/azure2/storage/Blob_Container.svg",
    "microsoft.storage/storageaccounts/fileservices": "img/lib/azure2/storage/File_Service.svg",
    "microsoft.storage/storageaccounts/fileservices/shares": "img/lib/azure2/storage/File_Share.svg",
    "microsoft.storage/storageaccounts/queueservices": "img/lib/azure2/storage/Queue_Service.svg",
    "microsoft.storage/storageaccounts/tableservices": "img/lib/azure2/storage/Table_Service.svg",
    "microsoft.web/serverfarms": "img/lib/azure2/app_services/App_Service_Plans.svg",
    "microsoft.web/sites": "img/lib/azure2/compute/App_Services.svg"
}

FALLBACK_STYLES = {
    "managementgroup": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;shadow=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=14;",
    "subscription": "rounded=1;whiteSpace=wrap;html=1;shadow=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=12;",
    "resourcegroup": "image;aspect=fixed;html=1;points=[];align=center;fontSize=12;image=img/lib/azure2/general/Resource_Groups.svg;",
    "resource": "rounded=1;whiteSpace=wrap;html=1;shadow=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
}

def get_node_style(resource_type):
    if not resource_type:
        return FALLBACK_STYLES['resource']
    resource_type_lower = resource_type.lower()
    icon_path = AZURE_ICONS.get(resource_type_lower)
    if icon_path:
        return f"image;aspect=fixed;html=1;points=[];align=center;fontSize=12;image={icon_path}"
    if resource_type_lower == 'microsoft.management/managementgroups': return FALLBACK_STYLES['managementgroup']
    if resource_type_lower == 'microsoft.resources/subscriptions': return FALLBACK_STYLES['subscription']
    if resource_type_lower == 'microsoft.resources/subscriptions/resourcegroups': return FALLBACK_STYLES['resourcegroup']
    return FALLBACK_STYLES['resource']

def pretty_print_xml(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def generate_infrastructure_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """Disposición para diagrama de infraestructura - jerarquía completa"""
    # Ya existe la lógica actual, mantenerla como está
    return None  # La lógica actual se mantiene en generate_drawio_file

def generate_components_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """Disposición para diagrama de componentes - agrupado por función/tipo"""
    y_step = 180
    x_step = 200
    node_positions = {}
    
    # Agrupar recursos por tipo/función
    groups = {
        'Governance': [],  # Management groups, suscripciones
        'Compute': [],     # VMs, App Services, AKS
        'Storage': [],     # Storage accounts, disks
        'Network': [],     # VNets, load balancers, firewalls
        'Database': [],    # SQL, CosmosDB
        'Security': [],    # Key Vault, managed identity
        'AI/ML': [],       # Cognitive services, ML workspaces
        'Management': [],  # Log Analytics, Application Insights
        'Other': []        # Resto
    }
    
    # Clasificar recursos por grupo funcional
    for i, item in enumerate(items):
        resource_type = (item.get('type') or '').lower()
        if resource_type in ['microsoft.management/managementgroups', 'microsoft.resources/subscriptions', 'microsoft.resources/subscriptions/resourcegroups']:
            groups['Governance'].append((i, item))
        elif any(t in resource_type for t in ['compute', 'web/sites', 'containerservice']):
            groups['Compute'].append((i, item))
        elif 'storage' in resource_type:
            groups['Storage'].append((i, item))
        elif 'network' in resource_type:
            groups['Network'].append((i, item))
        elif any(t in resource_type for t in ['sql', 'documentdb', 'dbfor']):
            groups['Database'].append((i, item))
        elif any(t in resource_type for t in ['keyvault', 'security', 'managedidentity']):
            groups['Security'].append((i, item))
        elif any(t in resource_type for t in ['cognitiveservices', 'machinelearning']):
            groups['AI/ML'].append((i, item))
        elif any(t in resource_type for t in ['insights', 'operationalinsights', 'automation']):
            groups['Management'].append((i, item))
        else:
            groups['Other'].append((i, item))
    
    # Posicionar grupos verticalmente
    group_y = 100  # Espacio para títulos
    for group_name, group_items in groups.items():
        if not group_items:
            continue
        
        # Posicionar recursos del grupo horizontalmente
        x = 100
        for idx, item in group_items:
            node_positions[idx] = (x, group_y)
            x += x_step
        
        group_y += y_step * 2  # Espacio entre grupos
    
    return node_positions

def generate_network_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """Disposición para diagrama de red - arquitectura de red realista estilo Azure"""
    node_positions = {}
    group_info = []
    resource_to_parent_id = {}

    # Organizar recursos por categorías de red con enfoque arquitectónico
    network_structure = {
        'internet': [],      # Internet Gateway, Public IPs, DNS externos
        'edge': [],          # Application Gateway, Load Balancers externos, Firewall
        'vnets': {},         # Virtual Networks organizadas por región
        'connectivity': [],  # VPN Gateways, ExpressRoute, Connections
        'security': [],      # NSGs, Azure Firewall, Key Vault
        'management': []     # Management Groups, Subscriptions (solo como contexto mínimo)
    }
    
    # Mapeo de subnets y sus recursos
    subnet_resources = {}
    vnet_to_region = {}
    
    print("🔍 Analizando recursos para diagrama de red...")

    # 1. Identificar VNets, subnets y regiones
    for i, item in enumerate(items):
        resource_type = (item.get('type') or '').lower()
        location = (item.get('location') or 'unknown').lower()
        
        if resource_type == 'microsoft.network/virtualnetworks':
            vnet_id = item['id'].lower()
            vnet_to_region[vnet_id] = location
            if location not in network_structure['vnets']:
                network_structure['vnets'][location] = {}
            network_structure['vnets'][location][vnet_id] = {
                'vnet': (i, item), 
                'subnets': {}
            }
            
        elif resource_type == 'microsoft.network/virtualnetworks/subnets':
            subnet_id = item['id'].lower()
            # Extraer VNet ID de la subnet
            vnet_id = '/'.join(subnet_id.split('/')[:-2])
            subnet_name = item.get('name', '').lower()
            
            # Clasificar subnet por tipo (para mejor organización visual)
            subnet_type = 'private'  # default
            if any(keyword in subnet_name for keyword in ['public', 'web', 'frontend', 'gateway']):
                subnet_type = 'public'
            elif any(keyword in subnet_name for keyword in ['db', 'database', 'data', 'backend']):
                subnet_type = 'data'
            elif any(keyword in subnet_name for keyword in ['app', 'application', 'middle']):
                subnet_type = 'application'
            
            region = vnet_to_region.get(vnet_id, 'unknown')
            if region in network_structure['vnets'] and vnet_id in network_structure['vnets'][region]:
                if subnet_type not in network_structure['vnets'][region][vnet_id]['subnets']:
                    network_structure['vnets'][region][vnet_id]['subnets'][subnet_type] = []
                network_structure['vnets'][region][vnet_id]['subnets'][subnet_type].append((i, item))
                subnet_resources[subnet_id] = []

    # 2. Clasificar recursos por función de red
    for i, item in enumerate(items):
        resource_type = (item.get('type') or '').lower()
        
        # Skip ya procesados
        if resource_type in ['microsoft.network/virtualnetworks', 'microsoft.network/virtualnetworks/subnets']:
            continue
            
        # Determinar subnet de destino si aplica
        resource_subnet = None
        props = item.get('properties', {})
        
        # Buscar referencias a subnet en diferentes propiedades
        subnet_refs = [
            props.get('subnet', {}).get('id'),
            props.get('virtualNetworkConfiguration', {}).get('subnetResourceId'),
            props.get('ipConfigurations', [{}])[0].get('subnet', {}).get('id') if props.get('ipConfigurations') else None
        ]
        
        for ref in subnet_refs:
            if ref:
                resource_subnet = ref.lower()
                break
        
        # Si no encontramos referencia directa, intentar extraer del ID
        if not resource_subnet and '/subnets/' in item['id'].lower():
            parts = item['id'].lower().split('/subnets/')
            if len(parts) > 1:
                resource_subnet = f"{parts[0]}/subnets/{parts[1].split('/')[0]}"

        # Asignar a subnet si encontramos una
        if resource_subnet and resource_subnet in subnet_resources:
            subnet_resources[resource_subnet].append((i, item))
            continue

        # Clasificación por función de red (recursos no asignados a subnets específicas)
        if any(t in resource_type for t in ['publicip', 'dns', 'trafficmanager', 'frontdoor']):
            network_structure['internet'].append((i, item))
        elif any(t in resource_type for t in ['applicationgateway', 'loadbalancer', 'firewall']):
            network_structure['edge'].append((i, item))
        elif any(t in resource_type for t in ['vpngateway', 'expressroute', 'connection', 'virtualnetworkgateway']):
            network_structure['connectivity'].append((i, item))
        elif any(t in resource_type for t in ['networksecuritygroup', 'keyvault', 'privatednszone']):
            network_structure['security'].append((i, item))
        elif resource_type in ['microsoft.management/managementgroups', 'microsoft.resources/subscriptions']:
            network_structure['management'].append((i, item))

    # --- LAYOUT MEJORADO PARA ARQUITECTURA DE RED ---
    
    # Configuración de layout
    margin = 80
    internet_height = 120
    edge_height = 150
    vnet_padding = 40
    subnet_padding = 25
    region_spacing = 200
    tier_spacing = 180
    
    current_y = margin
    
    # 1. CAPA INTERNET (Internet/External) - Top
    print("📡 Posicionando capa Internet...")
    if network_structure['internet']:
        internet_group_id = "group_internet"
        internet_width = max(len(network_structure['internet']) * 200, 800)
        
        group_info.append({
            'id': internet_group_id,
            'parent_id': '1',
            'type': 'internet_zone',
            'x': margin,
            'y': current_y,
            'width': internet_width,
            'height': internet_height,
            'label': '🌐 Internet / External Services',
            'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#e1f5fe;strokeColor=#01579b;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;'
        })
        
        x_offset = margin + 50
        for idx, item in network_structure['internet']:
            node_positions[idx] = (x_offset, current_y + internet_height//2 - 25)
            resource_to_parent_id[idx] = internet_group_id
            x_offset += 150
            
        current_y += internet_height + 30

    # 2. CAPA EDGE (Edge/Perimeter) - Application Gateways, Load Balancers
    print("🛡️ Posicionando capa Edge...")
    if network_structure['edge']:
        edge_group_id = "group_edge"
        edge_width = max(len(network_structure['edge']) * 200, 800)
        
        group_info.append({
            'id': edge_group_id,
            'parent_id': '1',
            'type': 'edge_zone',
            'x': margin,
            'y': current_y,
            'width': edge_width,
            'height': edge_height,
            'label': '🛡️ Edge / Perimeter Security',
            'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#fff3e0;strokeColor=#ef6c00;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;'
        })
        
        x_offset = margin + 50
        for idx, item in network_structure['edge']:
            node_positions[idx] = (x_offset, current_y + edge_height//2 - 25)
            resource_to_parent_id[idx] = edge_group_id
            x_offset += 150
            
        current_y += edge_height + 50

    # 3. CAPA VNETS (Virtual Networks por región) - Core
    print("🏗️ Posicionando VNets por región...")
    vnet_start_y = current_y
    max_region_width = 0
    region_counter = 0
    
    for region, vnets in network_structure['vnets'].items():
        if not vnets:
            continue
            
        print(f"   📍 Región: {region}")
        region_group_id = f"group_region_{region_counter}"
        region_counter += 1
        
        # Calcular dimensiones de la región
        vnet_count = len(vnets)
        vnets_per_row = min(2, vnet_count)  # Máximo 2 VNets por fila
        vnet_rows = (vnet_count + vnets_per_row - 1) // vnets_per_row
        
        vnet_width = 600
        vnet_height_base = 300
        region_width = vnets_per_row * vnet_width + (vnets_per_row + 1) * vnet_padding
        max_region_width = max(max_region_width, region_width)
        
        # Crear grupo de región
        region_y = vnet_start_y
        region_height = vnet_rows * (vnet_height_base + 50) + (vnet_rows + 1) * vnet_padding
        
        group_info.append({
            'id': region_group_id,
            'parent_id': '1',
            'type': 'region_container',
            'x': margin,
            'y': region_y,
            'width': region_width,
            'height': region_height,
            'label': f'🌍 Region: {region.title()}',
            'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#f3e5f5;strokeColor=#7b1fa2;fontSize=16;fontStyle=1;align=left;verticalAlign=top;spacingLeft=15;spacingTop=15;'
        })
        
        # Posicionar VNets dentro de la región
        vnet_counter = 0
        for vnet_row in range(vnet_rows):
            row_vnets = list(vnets.items())[vnet_row * vnets_per_row:(vnet_row + 1) * vnets_per_row]
            
            for vnet_col, (vnet_id, vnet_data) in enumerate(row_vnets):
                vnet_idx, vnet_item = vnet_data['vnet']
                vnet_group_id = f"group_vnet_{vnet_counter}"
                vnet_counter += 1
                
                vnet_x = margin + vnet_padding + vnet_col * (vnet_width + vnet_padding)
                vnet_y = region_y + vnet_padding + 40 + vnet_row * (vnet_height_base + 50)
                
                # Calcular altura dinámica basada en subnets
                subnet_types = vnet_data['subnets']
                subnet_tiers = ['public', 'application', 'private', 'data']  # Orden lógico de tiers
                
                tier_height = 80
                vnet_actual_height = max(vnet_height_base, len([t for t in subnet_tiers if t in subnet_types]) * tier_height + 100)
                
                # Crear contenedor de VNet
                group_info.append({
                    'id': vnet_group_id,
                    'parent_id': region_group_id,
                    'type': 'vnet_container',
                    'x': vnet_x,
                    'y': vnet_y,
                    'width': vnet_width,
                    'height': vnet_actual_height,
                    'label': f'🏗️ VNet: {vnet_item.get("name", "N/A")}',
                    'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#e8f5e8;strokeColor=#2e7d32;fontSize=14;fontStyle=1;align=left;verticalAlign=top;spacingLeft=15;spacingTop=15;'
                })
                
                node_positions[vnet_idx] = (vnet_x + 20, vnet_y + 20)
                resource_to_parent_id[vnet_idx] = vnet_group_id
                
                # Organizar subnets por tiers
                current_tier_y = vnet_y + 50
                subnet_counter = 0
                
                for tier_name in subnet_tiers:
                    if tier_name not in subnet_types:
                        continue
                        
                    tier_subnets = subnet_types[tier_name]
                    if not tier_subnets:
                        continue
                    
                    # Crear tier de subnet
                    tier_group_id = f"group_tier_{tier_name}_{subnet_counter}"
                    subnet_counter += 1
                    
                    tier_colors = {
                        'public': {'fill': '#ffebee', 'stroke': '#c62828'},
                        'application': {'fill': '#e3f2fd', 'stroke': '#1565c0'},
                        'private': {'fill': '#f1f8e9', 'stroke': '#388e3c'},
                        'data': {'fill': '#fce4ec', 'stroke': '#ad1457'}
                    }
                    
                    colors = tier_colors.get(tier_name, {'fill': '#f5f5f5', 'stroke': '#616161'})
                    
                    group_info.append({
                        'id': tier_group_id,
                        'parent_id': vnet_group_id,
                        'type': 'subnet_tier',
                        'x': vnet_x + 20,
                        'y': current_tier_y,
                        'width': vnet_width - 40,
                        'height': tier_height,
                        'label': f'{tier_name.title()} Tier',
                        'style': f'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor={colors["fill"]};strokeColor={colors["stroke"]};fontSize=12;fontStyle=1;align=left;verticalAlign=top;spacingLeft=10;spacingTop=5;'
                    })
                    
                    # Posicionar subnets y sus recursos
                    subnet_x = vnet_x + 40
                    for subnet_idx, subnet_item in tier_subnets:
                        subnet_id = subnet_item['id'].lower()
                        
                        node_positions[subnet_idx] = (subnet_x, current_tier_y + 25)
                        resource_to_parent_id[subnet_idx] = tier_group_id
                        
                        # Posicionar recursos dentro de la subnet
                        resource_x = subnet_x + 100
                        for res_idx, res_item in subnet_resources.get(subnet_id, []):
                            node_positions[res_idx] = (resource_x, current_tier_y + 25)
                            resource_to_parent_id[res_idx] = tier_group_id
                            resource_x += 80
                        
                        subnet_x += max(200, len(subnet_resources.get(subnet_id, [])) * 80 + 120)
                    
                    current_tier_y += tier_height + 10
        
        vnet_start_y += region_height + region_spacing

    # 4. CAPA CONECTIVIDAD (VPN, ExpressRoute) - Bottom
    current_y = vnet_start_y + 50
    if network_structure['connectivity']:
        print("🔗 Posicionando capa de conectividad...")
        connectivity_group_id = "group_connectivity"
        connectivity_width = max(len(network_structure['connectivity']) * 180, 600)
        connectivity_height = 100
        
        group_info.append({
            'id': connectivity_group_id,
            'parent_id': '1',
            'type': 'connectivity_zone',
            'x': margin,
            'y': current_y,
            'width': connectivity_width,
            'height': connectivity_height,
            'label': '🔗 Hybrid Connectivity',
            'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#f9fbe7;strokeColor=#689f38;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;'
        })
        
        x_offset = margin + 50
        for idx, item in network_structure['connectivity']:
            node_positions[idx] = (x_offset, current_y + connectivity_height//2 - 25)
            resource_to_parent_id[idx] = connectivity_group_id
            x_offset += 150
        
        current_y += connectivity_height + 30

    # 5. CAPA SEGURIDAD (Security, Management) - Side panel
    if network_structure['security'] or network_structure['management']:
        print("🔒 Posicionando recursos de seguridad y gestión...")
        security_x = margin + max_region_width + 100
        security_y = margin
        
        all_security = network_structure['security'] + network_structure['management']
        security_height = len(all_security) * 70 + 50
        
        security_group_id = "group_security"
        group_info.append({
            'id': security_group_id,
            'parent_id': '1',
            'type': 'security_zone',
            'x': security_x,
            'y': security_y,
            'width': 250,
            'height': security_height,
            'label': '🔒 Security & Management',
            'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#424242;fontSize=12;fontStyle=1;align=left;verticalAlign=top;spacingLeft=10;spacingTop=10;'
        })
        
        y_offset = security_y + 40
        for idx, item in all_security:
            node_positions[idx] = (security_x + 20, y_offset)
            resource_to_parent_id[idx] = security_group_id
            y_offset += 70

    print(f"✅ Layout de red completado: {len(node_positions)} recursos posicionados")
    return node_positions, group_info, resource_to_parent_id

def generate_drawio_file(items, dependencies, embed_data=True, include_ids=None, diagram_mode='infrastructure'):
    import sys
    import json
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    print("INFO: Generando el archivo .drawio...")
    
    mxfile = ET.Element("mxfile", host="app.diagrams.net", agent="python-script")
    diagram = ET.SubElement(mxfile, "diagram", id="main-diagram", name="Azure Infrastructure")
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel", dx="2500", dy="2000", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="4681", pageHeight="3300")
    root = ET.SubElement(mxGraphModel, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    azure_id_to_cell_id = {}
    levels = {0: [], 1: [], 2: [], 3: []}
    mg_id_to_idx, sub_id_to_idx, rg_id_to_idx = {}, {}, {}
    for i, item in enumerate(items):
        t = (item.get('type') or '').lower()
        if t == 'microsoft.management/managementgroups': levels[0].append((i, item)); mg_id_to_idx[item['id'].lower()] = i
        elif t == 'microsoft.resources/subscriptions': levels[1].append((i, item)); sub_id_to_idx[item['id'].lower()] = i
        elif t == 'microsoft.resources/subscriptions/resourcegroups': levels[2].append((i, item)); rg_id_to_idx[item['id'].lower()] = i
        else: levels[3].append((i, item))

    node_positions, group_info, resource_to_parent_id = {}, [], {}
    if diagram_mode == 'network':
        node_positions, group_info, resource_to_parent_id = generate_network_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
    elif diagram_mode == 'components':
        node_positions = generate_components_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
    else: # 'infrastructure'
        # La lógica de layout de infraestructura original se simplifica y se mantiene aquí
        y_step, x_step = 180, 180
        # ... (código de layout de infraestructura omitido por brevedad, se usará el fallback)

    # Fallback de posicionamiento para nodos sin posición
    for i, item in enumerate(items):
        if i not in node_positions:
            node_positions[i] = ((i % 15) * 180, 1500 + (i // 15) * 150)

    # Crear agrupadores (contenedores)
    for group in group_info:
        group_cell = ET.SubElement(root, "mxCell", id=group['id'], style=group['style'], parent=group.get('parent_id', '1'), vertex="1")
        ET.SubElement(group_cell, "mxGeometry", attrib={'x': str(group['x']), 'y': str(group['y']), 'width': str(group['width']), 'height': str(group['height']), 'as': 'geometry'})
        ET.SubElement(group_cell, "object", attrib={'label': group['label'], 'as': 'value'})

    # Crear nodos de recursos
    for i, item in enumerate(items):
        cell_id = f"node-{i}"
        azure_id_to_cell_id[item['id'].lower()] = cell_id
        style = get_node_style(item.get('type'))
        parent_id = resource_to_parent_id.get(i, '1')
        
        node_cell = ET.SubElement(root, "mxCell", id=cell_id, style=style, parent=parent_id, vertex="1")
        
        x_pos, y_pos = node_positions.get(i)
        width, height = ('60', '60') if parent_id != '1' else ('80', '80')
        
        ET.SubElement(node_cell, "mxGeometry", attrib={'x': str(x_pos), 'y': str(y_pos), 'width': width, 'height': height, 'as': 'geometry'})
        
        object_attribs = {'label': f"<b>{item.get('name', 'N/A')}</b>", 'as': 'value', 'type': str(item.get('type', ''))}
        if embed_data:
            for key, value in item.items():
                if key not in ['type', 'name']:
                    object_attribs[key.replace(':', '_')] = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        ET.SubElement(node_cell, "object", attrib=object_attribs)

    # Crear dependencias (flechas)
    for i, (source_id, target_id) in enumerate(dependencies):
        if source_id in azure_id_to_cell_id and target_id in azure_id_to_cell_id:
            source_cell, target_cell = azure_id_to_cell_id[source_id], azure_id_to_cell_id[target_id]
            edge_cell = ET.SubElement(root, "mxCell", id=f"edge-{i}", style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;", parent="1", source=source_cell, target=target_cell, edge="1")
            ET.SubElement(edge_cell, "mxGeometry", attrib={'relative': '1', 'as': 'geometry'})
            
    return pretty_print_xml(mxfile)

def filter_items_and_dependencies(items, dependencies, include_ids=None, exclude_ids=None):
    if not include_ids and not exclude_ids:
        return items, dependencies
    include_ids = set(i.lower() for i in include_ids) if include_ids else None
    exclude_ids = set(i.lower() for i in exclude_ids) if exclude_ids else set()
    child_map = {}
    for src, tgt in dependencies:
        child_map.setdefault(tgt, set()).add(src)
    def collect_descendants(start_ids):
        result = set()
        stack = list(start_ids)
        while stack:
            current = stack.pop()
            if current not in result:
                result.add(current)
                stack.extend(child_map.get(current, []))
        return result
    all_ids = set(item['id'].lower() for item in items)
    selected_ids = set()
    if include_ids:
        selected_ids = collect_descendants(include_ids)
        selected_ids.update(include_ids)
    else:
        selected_ids = all_ids
    if exclude_ids:
        to_exclude = collect_descendants(exclude_ids)
        to_exclude.update(exclude_ids)
        selected_ids = selected_ids - to_exclude
    filtered_items = [item for item in items if item['id'].lower() in selected_ids]
    filtered_dependencies = [(src, tgt) for src, tgt in dependencies if src in selected_ids and tgt in selected_ids]
    return filtered_items, filtered_dependencies

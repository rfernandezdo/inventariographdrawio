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
    "microsoft.network/applicationgateways": "img/lib/azure2/networking/Application_Gateways.svg",
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
    """Disposición para diagrama de infraestructura - árbol jerárquico usando dependencias estructurales"""
    print("🌳 Generando layout de árbol jerárquico usando dependencias estructurales...")
    
    node_positions = {}
    group_info = []
    resource_to_parent_id = {}
    tree_edges = []
    
    # Crear mapas de relaciones jerárquicas
    children_map = {}  # parent_id -> [child_ids]
    parent_map = {}    # child_id -> parent_id
    item_id_to_idx = {item['id'].lower(): i for i, item in enumerate(items)}
    
    # Inicializar mapas
    for i, item in enumerate(items):
        item_id = item['id'].lower()
        children_map[item_id] = []
    
    # FILTRAR SOLO DEPENDENCIAS JERÁRQUICAS ESTRUCTURALES DE AZURE
    print("🔍 Filtrando dependencias jerárquicas estructurales...")
    
    def is_hierarchical_dependency(src_item, tgt_item):
        """Determina si una dependencia es jerárquica estructural de Azure"""
        src_type = (src_item.get('type') or '').lower()
        tgt_type = (tgt_item.get('type') or '').lower()
        
        # MG -> MG (Management Group padre-hijo)
        if (src_type == 'microsoft.management/managementgroups' and 
            tgt_type == 'microsoft.management/managementgroups'):
            return True
        
        # Suscripción -> MG
        if (src_type == 'microsoft.resources/subscriptions' and 
            tgt_type == 'microsoft.management/managementgroups'):
            return True
        
        # RG -> Suscripción
        if (src_type == 'microsoft.resources/subscriptions/resourcegroups' and 
            tgt_type == 'microsoft.resources/subscriptions'):
            return True
        
        # Recurso -> RG
        if (src_type not in ['microsoft.management/managementgroups',
                            'microsoft.resources/subscriptions',
                            'microsoft.resources/subscriptions/resourcegroups'] and
            tgt_type == 'microsoft.resources/subscriptions/resourcegroups'):
            return True
        
        return False
    
    # Construir el árbol jerárquico usando SOLO dependencias estructurales
    hierarchical_count = 0
    for src_id, tgt_id in dependencies:
        src_id_lower, tgt_id_lower = src_id.lower(), tgt_id.lower()
        
        if src_id_lower in item_id_to_idx and tgt_id_lower in item_id_to_idx:
            src_item = items[item_id_to_idx[src_id_lower]]
            tgt_item = items[item_id_to_idx[tgt_id_lower]]
            
            if is_hierarchical_dependency(src_item, tgt_item):
                # La dependencia va de hijo a padre (src depende de tgt)
                children_map[tgt_id_lower].append(src_id_lower)
                parent_map[src_id_lower] = tgt_id_lower
                hierarchical_count += 1
    
    print(f"📊 Dependencias jerárquicas encontradas: {hierarchical_count}")
    
    # Conectar elementos huérfanos usando la estructura lógica de Azure
    print("🔧 Conectando elementos huérfanos usando estructura lógica de Azure...")
    
    # Crear nodo raíz virtual si no hay Management Groups
    virtual_root_created = False
    if not levels[0]:  # No hay Management Groups
        virtual_root_id = "azure_tenant_root"
        children_map[virtual_root_id] = []
        virtual_root_created = True
        
        # Conectar suscripciones huérfanas al nodo raíz virtual
        for idx, item in levels[1]:  # Suscripciones
            item_id = item['id'].lower()
            if item_id not in parent_map:
                children_map[virtual_root_id].append(item_id)
                parent_map[item_id] = virtual_root_id
    
    # Conectar suscripciones huérfanas al primer MG si existe
    if levels[0]:  # Hay Management Groups
        first_mg_id = levels[0][0][1]['id'].lower()
        for idx, item in levels[1]:  # Suscripciones
            item_id = item['id'].lower()
            if item_id not in parent_map:
                children_map[first_mg_id].append(item_id)
                parent_map[item_id] = first_mg_id
                print(f"   📋 Suscripción conectada a MG: {item['name']}")
    
    # Conectar RGs a sus suscripciones por ID
    for idx, item in levels[2]:  # Resource Groups
        item_id = item['id'].lower()
        if item_id not in parent_map:
            # Extraer suscripción del ID del RG
            rg_parts = item_id.split('/')
            if 'subscriptions' in rg_parts:
                sub_id = '/'.join(rg_parts[:rg_parts.index('resourcegroups')])
                if sub_id in item_id_to_idx:
                    children_map[sub_id].append(item_id)
                    parent_map[item_id] = sub_id
    
    # Conectar recursos a sus RGs por ID
    for idx, item in levels[3]:  # Recursos
        item_id = item['id'].lower()
        if item_id not in parent_map:
            # Extraer RG del ID del recurso
            resource_parts = item_id.split('/')
            if 'resourcegroups' in resource_parts:
                try:
                    rg_end_idx = resource_parts.index('resourcegroups') + 2
                    rg_id = '/'.join(resource_parts[:rg_end_idx])
                    if rg_id in item_id_to_idx:
                        children_map[rg_id].append(item_id)
                        parent_map[item_id] = rg_id
                    else:
                        # Buscar RG por nombre
                        rg_name = resource_parts[resource_parts.index('resourcegroups') + 1]
                        for rg_idx, rg_item in levels[2]:
                            if rg_item['name'].lower() == rg_name:
                                rg_id_alt = rg_item['id'].lower()
                                children_map[rg_id_alt].append(item_id)
                                parent_map[item_id] = rg_id_alt
                                break
                except IndexError:
                    pass  # ID mal formado, ignorar
    
    # Encontrar nodos raíz
    root_nodes = []
    if virtual_root_created:
        root_nodes = ["azure_tenant_root"]
    else:
        for item_id in item_id_to_idx:
            if item_id not in parent_map:
                root_nodes.append(item_id)
    
    print(f"🌱 Raíces encontradas: {len(root_nodes)}")
    
    # Configuración del árbol
    node_width = 120
    node_height = 80
    level_spacing = 150
    min_horizontal_spacing = 140
    
    # Función DFS para calcular el layout del árbol con protección contra recursión
    def calculate_tree_layout(node_id, level=0, start_x=0, visited=None):
        """Calcula el layout usando DFS y retorna el ancho total del subárbol"""
        
        if visited is None:
            visited = set()
        
        # Protección contra recursión infinita
        if node_id in visited:
            print(f"⚠️ Ciclo detectado, evitando recursión infinita en: {node_id}")
            return node_width
        
        visited.add(node_id)
        
        try:
            if node_id == "azure_tenant_root":
                # Crear grupo visual para el nodo raíz virtual
                group_info.append({
                    'id': 'azure_tenant_root',
                    'parent_id': '1',
                    'type': 'tenant_root',
                    'x': start_x,
                    'y': level * level_spacing + 50,
                    'width': 200,
                    'height': 80,
                    'label': '🏢 Azure Tenant (Root)',
                    'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#e1f5fe;strokeColor=#01579b;fontSize=16;fontStyle=1;align=center;verticalAlign=middle;'
                })
                
                # Procesar hijos del nodo virtual
                children = children_map.get(node_id, [])
                if not children:
                    return 200
                
                current_x = start_x
                total_width = 0
                
                for child_id in children:
                    child_width = calculate_tree_layout(child_id, level + 1, current_x, visited.copy())
                    current_x += child_width + min_horizontal_spacing
                    total_width += child_width + min_horizontal_spacing
                
                return max(200, total_width - min_horizontal_spacing if total_width > 0 else 200)
            
            # Nodo regular
            if node_id not in item_id_to_idx:
                return node_width
            
            node_idx = item_id_to_idx[node_id]
            current_item = items[node_idx]
            
            # Obtener hijos
            children = children_map.get(node_id, [])
            
            if not children:
                # Nodo hoja
                x = start_x + node_width // 2
                y = level * level_spacing + 100
                node_positions[node_idx] = (x, y)
                return node_width
            
            # Detectar si este es un Resource Group con recursos
            is_resource_group = current_item.get('type', '').lower() == 'microsoft.resources/subscriptions/resourcegroups'
            min_children_for_arc = 4  # Mínimo 4 recursos para usar layout en arco
            
            if is_resource_group and len(children) >= min_children_for_arc:
                # Layout en arco para Resource Groups con recursos
                print(f"📦 RG con {len(children)} recursos - usando layout en arco")
                
                import math
                
                # Configuración del arco (semicírculo debajo del RG) - ESPACIADO MÁXIMO
                min_radius = 250  # Radio mínimo muy aumentado para evitar solapamiento
                radius_per_resource = 30  # Espacio más generoso por recurso
                base_radius = max(min_radius, len(children) * radius_per_resource)
                
                # Espaciado adicional entre recursos (muy aumentado)
                min_arc_spacing = 0.5  # Ángulo mínimo entre recursos (en radianes) - más espaciado
                
                arc_center_x = start_x + base_radius + node_width // 2
                arc_center_y = level * level_spacing + 100  # RG en la parte superior
                
                # Calcular el arco necesario basado en el número de recursos (ARCO HACIA ABAJO)
                if len(children) == 1:
                    # Un solo recurso: directamente debajo
                    start_angle = math.pi  # Abajo del todo
                    end_angle = math.pi
                elif len(children) <= 3:
                    # Pocos recursos: arco pequeño centrado hacia abajo
                    total_arc = min_arc_spacing * (len(children) - 1)
                    center_angle = math.pi  # Centro del arco (abajo)
                    start_angle = center_angle - total_arc / 2
                    end_angle = center_angle + total_arc / 2
                else:
                    # Muchos recursos: usar semicírculo hacia abajo
                    max_arc = math.pi * 0.8  # Máximo 80% de semicírculo
                    needed_arc = min_arc_spacing * (len(children) - 1)
                    actual_arc = min(max_arc, needed_arc)
                    center_angle = math.pi  # Centro del arco (abajo)
                    start_angle = center_angle - actual_arc / 2
                    end_angle = center_angle + actual_arc / 2
                
                # Calcular posiciones en arco con espaciado mejorado
                for i, child_id in enumerate(children):
                    if child_id in item_id_to_idx:
                        if len(children) == 1:
                            # Un solo recurso: directamente debajo del RG
                            child_x = arc_center_x
                            child_y = arc_center_y + base_radius  # Directamente debajo
                        else:
                            # Distribución uniforme en el arco calculado - ARCO HACIA ABAJO
                            arc_span = end_angle - start_angle
                            if len(children) == 2:
                                # Dos recursos: uno a cada lado del centro inferior
                                angle = start_angle + (i + 0.5) * arc_span / len(children)
                            else:
                                # Múltiples recursos: distribución uniforme en el arco hacia abajo
                                angle = start_angle + (i * arc_span / (len(children) - 1))
                            
                            # Calcular posición en el arco (semicírculo hacia ABAJO del RG)
                            child_x = arc_center_x + base_radius * math.sin(angle)
                            child_y = arc_center_y + base_radius * (1 - math.cos(angle))  # Arco hacia abajo desde el RG
                            
                            # Asegurar que nunca está en la misma posición que el RG
                            if abs(child_x - arc_center_x) < 10 and abs(child_y - arc_center_y) < 10:
                                child_y = arc_center_y + base_radius  # Forzar posición debajo
                        
                        child_idx = item_id_to_idx[child_id]
                        node_positions[child_idx] = (child_x, child_y)
                
                # Posicionar el Resource Group en la parte superior del arco
                node_positions[node_idx] = (arc_center_x, arc_center_y)
                
                # Ancho total necesario para el layout en arco (muy aumentado)
                total_width = 2.5 * (base_radius + node_width + 80)  # Padding muy generoso
                return total_width
            
            else:
                # Layout lineal estándar para otros casos
                current_x = start_x
                children_widths = []
                
                # Calcular layout de todos los hijos
                for child_id in children:
                    child_width = calculate_tree_layout(child_id, level + 1, current_x, visited.copy())
                    children_widths.append(child_width)
                    current_x += child_width + min_horizontal_spacing
                
                # Ancho total del subárbol
                total_subtree_width = sum(children_widths) + min_horizontal_spacing * (len(children) - 1) if children else node_width
                
                # Posicionar el nodo padre en el centro de sus hijos
                parent_x = start_x + max(total_subtree_width // 2, node_width // 2)
                parent_y = level * level_spacing + 100
                node_positions[node_idx] = (parent_x, parent_y)
                
                return max(node_width, total_subtree_width)
            
        finally:
            visited.discard(node_id)
    
    # Procesar cada árbol raíz
    if not root_nodes:
        print("⚠️ No se encontraron nodos raíz, usando fallback")
        # Fallback: crear layout simple por niveles
        current_y = 100
        for level_num in [0, 1, 2, 3]:
            if level_num in levels:
                current_x = 100
                for idx, item in levels[level_num]:
                    node_positions[idx] = (current_x, current_y)
                    current_x += 150
                current_y += 150
    else:
        print(f"🌳 Procesando {len(root_nodes)} árbol(es) raíz...")
        start_x = 100
        
        for root_id in root_nodes:
            print(f"🌱 Procesando árbol con raíz: {root_id}")
            tree_width = calculate_tree_layout(root_id, 0, start_x)
            start_x += tree_width + 200  # Espaciado entre árboles diferentes
    
    # Crear conexiones para el árbol jerárquico
    for child_id, parent_id in parent_map.items():
        if child_id in item_id_to_idx and parent_id != "azure_tenant_root":
            if parent_id in item_id_to_idx:
                tree_edges.append((child_id, parent_id))
    
    print(f"✅ Layout jerárquico completado: {len(node_positions)} recursos posicionados")
    return node_positions, group_info, resource_to_parent_id, tree_edges

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
    tree_edges = []  # Para almacenar las conexiones del árbol
    
    if diagram_mode == 'network':
        node_positions, group_info, resource_to_parent_id = generate_network_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
    elif diagram_mode == 'components':
        node_positions = generate_components_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
    else: # 'infrastructure'
        node_positions, group_info, resource_to_parent_id, tree_edges = generate_infrastructure_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)

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
    edges_to_create = []
    
    if diagram_mode == 'infrastructure' and tree_edges:
        # Para el modo infrastructure, usar las conexiones del árbol DFS
        print(f"🔗 Usando {len(tree_edges)} conexiones de árbol jerárquico")
        item_id_to_idx = {item['id'].lower(): i for i, item in enumerate(items)}
        
        for child_id, parent_id in tree_edges:
            # child_id y parent_id son IDs de Azure, convertir a índices
            if child_id in item_id_to_idx and parent_id in item_id_to_idx:
                edges_to_create.append((child_id, parent_id))  # De hijo a padre para mostrar jerarquía
    else:
        # Para otros modos, usar las dependencias originales
        edges_to_create = dependencies
    
    # Agregar también las dependencias no jerárquicas como líneas punteadas en modo infrastructure
    if diagram_mode == 'infrastructure':
        print(f"🔗 Agregando {len(dependencies)} dependencias adicionales como relaciones")
        # Filtrar dependencias que no son jerárquicas para mostrarlas como relaciones
        hierarchical_pairs = set(tree_edges) if tree_edges else set()
        
        for src_id, tgt_id in dependencies:
            dependency_pair = (src_id.lower(), tgt_id.lower())
            reverse_pair = (tgt_id.lower(), src_id.lower())
            
            # Solo agregar si no es una dependencia jerárquica
            if dependency_pair not in hierarchical_pairs and reverse_pair not in hierarchical_pairs:
                edges_to_create.append((src_id, tgt_id))
    
    edge_counter = 0
    for source_id, target_id in edges_to_create:
        source_id_lower = source_id.lower()
        target_id_lower = target_id.lower()
        
        if source_id_lower in azure_id_to_cell_id and target_id_lower in azure_id_to_cell_id:
            source_cell = azure_id_to_cell_id[source_id_lower]
            target_cell = azure_id_to_cell_id[target_id_lower]
            
            # Determinar estilo de la flecha
            is_hierarchical = False
            is_rg_to_resource = False
            
            if diagram_mode == 'infrastructure' and tree_edges:
                is_hierarchical = (source_id_lower, target_id_lower) in [(c, p) for c, p in tree_edges]
                
                # Identificar si es una conexión RG → Resource específicamente
                if is_hierarchical:
                    # Buscar los items correspondientes
                    source_item = None
                    target_item = None
                    for item in items:
                        if item['id'].lower() == source_id_lower:
                            source_item = item
                        elif item['id'].lower() == target_id_lower:
                            target_item = item
                    
                    # Verificar si es RG → Resource (parent → child en tree_edges)
                    if target_item and source_item:
                        target_type = target_item.get('type', '').lower()
                        source_type = source_item.get('type', '').lower()
                        
                        # RG es el padre (target) y el recurso es el hijo (source)
                        is_rg_to_resource = (target_type == 'microsoft.resources/subscriptions/resourcegroups' and 
                                           source_type not in ['microsoft.management/managementgroups', 
                                                             'microsoft.resources/subscriptions',
                                                             'microsoft.resources/subscriptions/resourcegroups'])
            
            if is_hierarchical and is_rg_to_resource:
                # Conexión RG → Resource - línea sólida RECTA
                style = "edgeStyle=straight;rounded=0;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
            elif is_hierarchical:
                # Otras conexiones jerárquicas (MG → Sub, Sub → RG, MG → MG) - línea sólida ORTOGONAL
                style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
            else:
                # Dependencia no jerárquica - línea punteada ortogonal
                style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#757575;strokeWidth=1;dashed=1;"
            
            edge_cell = ET.SubElement(root, "mxCell", id=f"edge-{edge_counter}", style=style, parent="1", source=source_cell, target=target_cell, edge="1")
            ET.SubElement(edge_cell, "mxGeometry", attrib={'relative': '1', 'as': 'geometry'})
            edge_counter += 1
            
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

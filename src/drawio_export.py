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
    "microsoft.network/privatednszones": "img/lib/azure2/networking/DNS_Zones.svg",
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
        'management': [],    # Management Groups, Subscriptions (solo como contexto mínimo)
        'resource_groups': {}  # Resource Groups para organizar recursos
    }
    
    # Mapeo de subnets y sus recursos
    subnet_resources = {}
    vnet_to_region = {}
    resource_group_map = {}  # Mapa de RG ID -> info del RG
    
    print("🔍 Analizando recursos para diagrama de red...")

    # 0. Primero identificar Resource Groups para crear la jerarquía
    for i, item in enumerate(items):
        resource_type = (item.get('type') or '').lower()
        
        if resource_type == 'microsoft.resources/subscriptions/resourcegroups':
            rg_id = item['id'].lower()
            location = (item.get('location') or 'unknown').lower()
            resource_group_map[rg_id] = {
                'index': i,
                'item': item,
                'location': location,
                'resources': []  # Recursos que pertenecen a este RG
            }
            
            # Organizar RGs por región
            if location not in network_structure['resource_groups']:
                network_structure['resource_groups'][location] = {}
            network_structure['resource_groups'][location][rg_id] = resource_group_map[rg_id]

    # 1. Identificar VNets, subnets y regiones
    for i, item in enumerate(items):
        resource_type = (item.get('type') or '').lower()
        location = (item.get('location') or 'unknown').lower()
        
        # Skip resource groups ya procesados
        if resource_type == 'microsoft.resources/subscriptions/resourcegroups':
            continue
        
        if resource_type == 'microsoft.network/virtualnetworks':
            vnet_id = item['id'].lower()
            vnet_to_region[vnet_id] = location
            if location not in network_structure['vnets']:
                network_structure['vnets'][location] = {}
            network_structure['vnets'][location][vnet_id] = {
                'vnet': (i, item), 
                'subnets': {}
            }
            
            # Asignar VNet a su Resource Group
            vnet_rg_id = '/'.join(vnet_id.split('/')[:5])  # Extraer RG ID del VNet ID
            if vnet_rg_id in resource_group_map:
                resource_group_map[vnet_rg_id]['resources'].append((i, item))
            
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
                
            # Asignar subnet a su Resource Group
            subnet_rg_id = '/'.join(subnet_id.split('/')[:5])  # Extraer RG ID del subnet ID
            if subnet_rg_id in resource_group_map:
                resource_group_map[subnet_rg_id]['resources'].append((i, item))

    # 2. Clasificar recursos por función de red
    for i, item in enumerate(items):
        resource_type = (item.get('type') or '').lower()
        
        # Skip ya procesados
        if resource_type in ['microsoft.network/virtualnetworks', 'microsoft.network/virtualnetworks/subnets', 'microsoft.resources/subscriptions/resourcegroups']:
            continue
            
        # Asignar recurso a su Resource Group
        resource_id = item['id'].lower()
        resource_rg_id = '/'.join(resource_id.split('/')[:5])  # Extraer RG ID
        if resource_rg_id in resource_group_map:
            resource_group_map[resource_rg_id]['resources'].append((i, item))
            
        # Determinar subnet de destino si aplica
        resource_subnet = None
        props = item.get('properties', {})
        
        # Buscar referencias a subnet en diferentes propiedades
        subnet_refs = [
            props.get('subnet', {}).get('id'),
            props.get('virtualNetworkConfiguration', {}).get('subnetResourceId'),
            props.get('ipConfigurations', [{}])[0].get('subnet', {}).get('id') if props.get('ipConfigurations') else None
        ]
        
        # Para VMs, intentar inferir subnet desde network interfaces
        if resource_type == 'microsoft.compute/virtualmachines':
            network_profile = props.get('networkProfile', {})
            network_interfaces = network_profile.get('networkInterfaces', [])
            if network_interfaces:
                # Tomar la primera NIC para inferir subnet
                first_nic_id = network_interfaces[0].get('id', '')
                if first_nic_id:
                    # Inferir que la NIC probablemente está en la subnet 'compute' del mismo RG
                    # Esto es una heurística basada en naming conventions comunes
                    parts = resource_id.split('/')
                    if len(parts) >= 5:
                        subscription_id = parts[2]
                        rg_name = parts[4]
                        # Buscar subnets que contengan 'compute' en el mismo RG
                        for subnet_id in subnet_resources.keys():
                            if subscription_id in subnet_id and rg_name in subnet_id and 'compute' in subnet_id.lower():
                                resource_subnet = subnet_id
                                print(f"🔗 VM {item.get('name')} asociada a subnet {resource_subnet} por heurística")
                                break
        
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
            # Asignar subnet_id al item para usarlo después en el layout
            item['subnet_id'] = resource_subnet
            continue

        # Para recursos NO asignados a subnets, clasificar por función pero MANTENER asociación con RG
        # (Los recursos seguirán perteneciendo a su RG, solo se usan estas categorías para layout adicional)
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
        # NOTA: Todos los recursos siguen asignados a sus RGs, estas clasificaciones son solo para layout adicional

    # --- LAYOUT MEJORADO PARA ARQUITECTURA DE RED JERÁRQUICA ---
    
    # Configuración de layout
    margin = 80
    subscription_padding = 40
    rg_padding = 50  # Aumentado de 30 a 50px para mejor separación de los RGs del borde del contenedor
    vnet_padding = 20
    subnet_padding = 15
    
    current_y = margin
    
    # 1. MANAGEMENT GROUPS & SUBSCRIPTIONS (Panel lateral como referencia)
    print("📋 Posicionando Management Groups y Subscriptions...")
    mgmt_x = 50
    mgmt_y = margin
    mgmt_width = 300
    
    mgmt_security = network_structure['security'] + network_structure['management']
    if mgmt_security:
        # Calcular altura con mejor espaciado (100px por elemento + margen)
        mgmt_height = max(900, len(mgmt_security) * 100 + 150)  # Mínimo 900px, espaciado de 100px
        
        mgmt_group_id = "group_management"
        group_info.append({
            'id': mgmt_group_id,
            'parent_id': '1',
            'type': 'management_zone',
            'x': mgmt_x,
            'y': mgmt_y,
            'width': mgmt_width,
            'height': mgmt_height,
            'label': '📋 Management & Governance',
            'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;align=left;verticalAlign=top;spacingLeft=15;spacingTop=15;'
        })
        
        # Centrar horizontalmente los elementos en el contenedor (300px de ancho, iconos de 60px)
        # Posición X = (300 - 60) / 2 = 120
        center_x = (mgmt_width - 60) // 2  # 120px para centrar iconos de 60px en contenedor de 300px
        y_offset = 60  # Inicio con más margen superior
        
        for idx, item in mgmt_security:
            node_positions[idx] = (center_x, y_offset)
            resource_to_parent_id[idx] = mgmt_group_id
            y_offset += 100  # Separación vertical mejorada de 100px
    
    # 2. CONTAINERS POR SUBSCRIPTION
    print("🏢 Creando containers por Subscription...")
    subscription_start_x = mgmt_x + mgmt_width + 150  # Aumentado de 100 a 150px de separación
    
    # Obtener todas las subscriptions únicas
    subscriptions = {}
    for i, item in enumerate(items):
        if item.get('type', '').lower() == 'microsoft.resources/subscriptions':
            sub_id = item['id'].lower()
            subscriptions[sub_id] = {'index': i, 'item': item, 'resource_groups': {}}
    
    # Si no hay subscriptions explícitas, usar la subscription de los RGs
    if not subscriptions:
        # Crear subscription implícita basada en los RGs
        for rg_id, rg_data in resource_group_map.items():
            # Extraer subscription ID del RG ID
            sub_id = '/'.join(rg_id.split('/')[:3])  # /subscriptions/{sub-id}
            if sub_id not in subscriptions:
                subscriptions[sub_id] = {
                    'index': None,  # No hay item explícito
                    'item': {'id': sub_id, 'name': sub_id.split('/')[-1][:8] + '...'},
                    'resource_groups': {}
                }
            subscriptions[sub_id]['resource_groups'][rg_id] = rg_data
    else:
        # Asignar RGs a subscriptions existentes
        for rg_id, rg_data in resource_group_map.items():
            sub_id = '/'.join(rg_id.split('/')[:3])  # /subscriptions/{sub-id}
            if sub_id in subscriptions:
                subscriptions[sub_id]['resource_groups'][rg_id] = rg_data
    
    global_sub_counter = 0
    global_rg_counter = 0
    global_vnet_counter = 0
    global_subnet_counter = 0
    
    for sub_id, sub_data in subscriptions.items():
        if not sub_data['resource_groups']:  # Skip subs sin RGs
            continue
            
        print(f"   📁 Subscription: {sub_data['item'].get('name', 'N/A')}")
        
        # Calcular dimensiones del container de subscription dinámicamente
        rg_count = len(sub_data['resource_groups'])
        rgs_per_row = 2  # 2 RGs por fila
        rg_rows = (rg_count + rgs_per_row - 1) // rgs_per_row
        
        # Calcular dimensiones basadas en el contenido real de los RGs
        max_rg_width = 800   # Ancho máximo por RG (mucho más generoso)
        max_rg_height = 900  # Altura máxima por RG (mucho más generoso)
        
        sub_width = rgs_per_row * max_rg_width + (rgs_per_row + 1) * rg_padding
        sub_height = rg_rows * max_rg_height + (rg_rows + 1) * rg_padding + 60  # +60 para header
        
        sub_group_id = f"group_subscription_{global_sub_counter}"
        global_sub_counter += 1
        
        sub_x = subscription_start_x
        sub_y = current_y
        
        # Crear container de subscription
        group_info.append({
            'id': sub_group_id,
            'parent_id': '1',
            'type': 'subscription_container',
            'x': sub_x,
            'y': sub_y,
            'width': sub_width,
            'height': sub_height,
            'label': f'🏢 Subscription: {sub_data["item"].get("name", "N/A")}',
            'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#e3f2fd;strokeColor=#1976d2;fontSize=16;fontStyle=1;align=left;verticalAlign=top;spacingLeft=15;spacingTop=15;'
        })
        
        # Posicionar subscription item si existe
        if sub_data['index'] is not None:
            node_positions[sub_data['index']] = (20, 25)
            resource_to_parent_id[sub_data['index']] = sub_group_id
        
        # 3. CONTAINERS POR RESOURCE GROUP dentro de la subscription
        print(f"      📦 Creando {len(sub_data['resource_groups'])} Resource Groups...")
        
        rg_counter = 0
        current_row_height = 0  # Altura acumulada de la fila actual
        row_rg_heights = []  # Lista para almacenar las alturas de RGs en la fila actual
        
        for rg_id, rg_data in sub_data['resource_groups'].items():
            rg_row = rg_counter // rgs_per_row
            rg_col = rg_counter % rgs_per_row
            
            # Si es el primer RG de una nueva fila, calcular la posición Y
            if rg_col == 0 and rg_counter > 0:
                # Usar la altura máxima de la fila anterior
                max_height_prev_row = max(row_rg_heights) if row_rg_heights else max_rg_height
                current_row_height += max_height_prev_row + rg_padding
                row_rg_heights = []  # Reset para la nueva fila
            
            rg_x = rg_padding + rg_col * (max_rg_width + rg_padding)
            rg_y = 60 + rg_padding + current_row_height  # +60 para header de subscription
            
            rg_group_id = f"group_rg_{global_rg_counter}"
            global_rg_counter += 1
            rg_counter += 1
            
            # Analizar recursos del RG para calcular layout interno
            vnet_resources = []
            subnet_resources_by_vnet = {}
            standalone_resources = []
            
            for res_idx, res_item in rg_data['resources']:
                res_type = res_item.get('type', '').lower()
                
                if res_type == 'microsoft.network/virtualnetworks':
                    vnet_resources.append((res_idx, res_item))
                    vnet_id = res_item['id'].lower()
                    subnet_resources_by_vnet[vnet_id] = []
                elif res_type == 'microsoft.network/virtualnetworks/subnets':
                    # Encontrar VNet padre
                    subnet_id = res_item['id'].lower()
                    vnet_id = '/'.join(subnet_id.split('/')[:-2])
                    if vnet_id not in subnet_resources_by_vnet:
                        subnet_resources_by_vnet[vnet_id] = []
                    subnet_resources_by_vnet[vnet_id].append((res_idx, res_item))
                else:
                    # Verificar si está asociado a una subnet
                    associated_to_subnet = False
                    for subnet_id, subnet_res_list in subnet_resources.items():
                        if (res_idx, res_item) in subnet_res_list:
                            associated_to_subnet = True
                            break
                    
                    if not associated_to_subnet:
                        standalone_resources.append((res_idx, res_item))
            
            # Calcular dimensiones dinámicas del RG basadas en contenido
            rg_min_width = 400
            rg_min_height = 300  # Altura mínima más razonable para mostrar recursos
            rg_padding_internal = 20
            
            # Espacio para header del RG (nombre + icono)
            rg_content_height = 70  # Header space
            rg_content_width = rg_min_width
            
            # Calcular espacio para VNets
            vnet_height_total = 0
            if vnet_resources:
                for vnet_idx, vnet_item in vnet_resources:
                    vnet_id = vnet_item['id'].lower()
                    vnet_subnets = subnet_resources_by_vnet.get(vnet_id, [])
                    
                    # Altura VNet = header + (número de subnets * altura_subnet) + padding muy generoso
                    vnet_height = 120 + len(vnet_subnets) * 220 + 50  # Mucho más espacio: 220px por subnet + padding generoso
                    vnet_height_total += vnet_height + 60  # Mucho más espacio entre VNets
                    
                    # Ancho VNet (calculado dinámicamente basado en las subnets)
                    max_subnet_width_in_vnet = 0
                    for subnet_id in vnet_subnets:
                        subnet_resources_filtered = [(r_idx, r) for r_idx, r in rg_data['resources'] if r.get('subnet_id') == subnet_id]
                        resource_count = len(subnet_resources_filtered)
                        needed_subnet_width = max(400, 200 + resource_count * 120)
                        max_subnet_width_in_vnet = max(max_subnet_width_in_vnet, needed_subnet_width)
                    
                    # VNet debe ser al menos 120px más ancha que la subnet más grande
                    vnet_width_needed = max(600, max_subnet_width_in_vnet + 120)
                    rg_content_width = max(rg_content_width, vnet_width_needed + 80)  # +80px para margen en RG
                
                rg_content_height += vnet_height_total
            
            # Calcular espacio para recursos standalone con mejor distribución
            if standalone_resources:
                # Primero calculamos un ancho tentativo basado en el contenido
                tentative_width = max(rg_min_width, min(len(standalone_resources) * 120 + 80, 700))
                resources_per_row = max(1, min(3, (tentative_width - 80) // 120))  # 3 recursos máximo por fila
                standalone_rows = (len(standalone_resources) + resources_per_row - 1) // resources_per_row
                standalone_height = standalone_rows * 100 + 80  # 100px por fila + padding extra
                rg_content_height += standalone_height
                
                # Ancho para recursos standalone 
                standalone_width = min(len(standalone_resources), resources_per_row) * 120 + 80  # 120px por recurso + padding
                rg_content_width = max(rg_content_width, standalone_width)
            
            # Si no hay contenido significativo, usar tamaño mínimo pero razonable
            if not vnet_resources and len(standalone_resources) <= 1:
                rg_content_height = max(rg_min_height, 250)  # Al menos 250px para RGs pequeños
                rg_content_width = max(rg_min_width, 450)   # Al menos 450px de ancho
            
            # Aplicar tamaños mínimos y máximos más generosos
            rg_final_width = max(rg_min_width, min(rg_content_width, 800))   # Máximo 800px (mucho más ancho)
            rg_final_height = max(rg_min_height, min(rg_content_height, 900)) # Máximo 900px (mucho más alto)
            
            # Crear container de Resource Group con dimensiones dinámicas
            group_info.append({
                'id': rg_group_id,
                'parent_id': sub_group_id,
                'type': 'resource_group_container',
                'x': rg_x,
                'y': rg_y,
                'width': rg_final_width,
                'height': rg_final_height,
                'label': f'📦 RG: {rg_data["item"].get("name", "N/A")}',
                'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#fff8e1;strokeColor=#ff8f00;fontSize=14;fontStyle=1;align=left;verticalAlign=top;spacingLeft=10;spacingTop=10;'
            })
            
            # Posicionar el Resource Group en sí
            rg_idx = rg_data['index']
            node_positions[rg_idx] = (15, 25)
            resource_to_parent_id[rg_idx] = rg_group_id
            
            current_rg_y = 100  # Aumentado de 60 a 100px para evitar solapamiento con el icono del RG
            
            # 4. CONTAINERS DE VNETs dentro del RG (con mejor espaciado)
            for vnet_idx, vnet_item in vnet_resources:
                vnet_id = vnet_item['id'].lower()
                vnet_subnets = subnet_resources_by_vnet.get(vnet_id, [])
                
                vnet_group_id = f"group_vnet_{global_vnet_counter}"
                global_vnet_counter += 1
                
                # Calcular dimensiones dinámicas de VNet con espaciado muy generoso
                subnet_count = len(vnet_subnets)
                # Calcular ancho necesario basado en las subnets que contendrá
                max_subnet_width = 0
                for subnet_id in vnet_subnets:
                    subnet_resources_filtered = [(r_idx, r) for r_idx, r in rg_data['resources'] if r.get('subnet_id') == subnet_id]
                    resource_count = len(subnet_resources_filtered)
                    needed_subnet_width = max(400, 200 + resource_count * 120)
                    max_subnet_width = max(max_subnet_width, needed_subnet_width)
                
                # VNet debe ser al menos 120px más ancha que la subnet más grande (60px margen a cada lado)
                vnet_width = max(600, max_subnet_width + 120)
                vnet_height = max(200, 120 + subnet_count * 220)  # Mucho más espacio: 220px por subnet + header
                
                # Crear container de VNet
                group_info.append({
                    'id': vnet_group_id,
                    'parent_id': rg_group_id,
                    'type': 'vnet_container',
                    'x': 40,  # Aumentado de 20 a 40px para evitar solapamiento con el icono del RG
                    'y': current_rg_y,
                    'width': vnet_width,
                    'height': vnet_height,
                    'label': f'🏗️ VNet: {vnet_item.get("name", "N/A")}',
                    'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#e8f5e8;strokeColor=#2e7d32;fontSize=12;fontStyle=1;align=left;verticalAlign=top;spacingLeft=10;spacingTop=10;'
                })
                
                # Posicionar VNet
                node_positions[vnet_idx] = (15, 20)
                resource_to_parent_id[vnet_idx] = vnet_group_id
                
                # 5. CONTAINERS DE SUBNETs dentro de la VNet (con mejor espaciado)
                subnet_y = 60  # Aumentado de 50 a 60px para más separación desde el header de la VNet
                for subnet_idx, subnet_item in vnet_subnets:
                    subnet_id = subnet_item['id'].lower()
                    # Obtener recursos asociados con esta subnet específica (conservar tuplas completas)
                    current_subnet_resources = [(r_idx, r) for r_idx, r in rg_data['resources'] if r.get('subnet_id') == subnet_id]
                    
                    subnet_group_id = f"group_subnet_{global_subnet_counter}"
                    global_subnet_counter += 1
                    
                    # Calcular dimensiones dinámicas de subnet con más espacio generoso
                    resource_count = len(current_subnet_resources)
                    # Ancho ajustado para caber dentro de VNet - máximo VNet_width - 120px de margen (60px cada lado)
                    subnet_width = max(400, min(200 + resource_count * 120, vnet_width - 120))
                    # Altura muy generosa para evitar cualquier solapamiento
                    rows_needed = max(1, (resource_count + 1) // 2) if resource_count > 0 else 1  # 2 recursos por fila máximo
                    subnet_height = max(160, 120 + rows_needed * 90)  # Altura aún más generosa
                    
                    # Crear container de Subnet - centrado con 60px de margen mínimo a cada lado
                    subnet_x = max(60, (vnet_width - subnet_width) // 2)  # Centrar pero con margen mínimo de 60px
                    group_info.append({
                        'id': subnet_group_id,
                        'parent_id': vnet_group_id,
                        'type': 'subnet_container',
                        'x': subnet_x,
                        'y': subnet_y,
                        'width': subnet_width,
                        'height': subnet_height,
                        'label': f'Subnet: {subnet_item.get("name", "N/A")}',
                        'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#f3e5f5;strokeColor=#7b1fa2;fontSize=10;fontStyle=1;align=left;verticalAlign=top;spacingLeft=5;spacingTop=5;'
                    })
                    
                    # Posicionar Subnet
                    node_positions[subnet_idx] = (10, 25)
                    resource_to_parent_id[subnet_idx] = subnet_group_id
                    
                    # Posicionar recursos asociados a la subnet con espaciado muy generoso
                    resource_x = 80   # Mucho más margen desde el borde izquierdo para evitar solapamiento con icono subnet
                    resource_y = 70   # Más abajo para evitar solapamiento con título
                    resources_per_row = max(1, min(2, (subnet_width - 160) // 150))  # Máximo 2 recursos por fila, 150px por recurso
                    
                    for i, (res_idx, res_item) in enumerate(current_subnet_resources):
                        col = i % resources_per_row
                        row = i // resources_per_row
                        
                        x_pos = resource_x + col * 150  # Espaciado horizontal aún más generoso
                        y_pos = resource_y + row * 80   # Espaciado vertical aún más generoso
                        
                        node_positions[res_idx] = (x_pos, y_pos)
                        resource_to_parent_id[res_idx] = subnet_group_id
                    
                    subnet_y += subnet_height + 40  # Espaciado muy generoso entre subnets
                
                current_rg_y += vnet_height + 60  # Espaciado muy generoso entre VNets y recursos standalone
            
            # 6. RECURSOS NO VINCULADOS directamente en el RG (con mejor espaciado)
            if standalone_resources:
                standalone_x = 40  # Más margen desde el borde izquierdo
                standalone_y = current_rg_y + 40  # Más separación desde VNets
                
                resource_counter = 0
                resources_per_row = max(1, min(3, (rg_final_width - 80) // 120))  # Solo 3 recursos por fila, más espacio
                
                for res_idx, res_item in standalone_resources:
                    col = resource_counter % resources_per_row
                    row = resource_counter // resources_per_row
                    
                    x_pos = standalone_x + col * 120  # Espaciado de 120px horizontal
                    y_pos = standalone_y + row * 100   # Espaciado de 100px vertical
                    
                    node_positions[res_idx] = (x_pos, y_pos)
                    resource_to_parent_id[res_idx] = rg_group_id
                    resource_counter += 1
            
            # Agregar la altura de este RG a la fila actual
            row_rg_heights.append(rg_final_height)
            rg_counter += 1
        
        # Calcular la altura real de la subscription basada en el contenido
        if row_rg_heights:
            final_row_height = max(row_rg_heights)
            actual_sub_height = 60 + rg_padding + current_row_height + final_row_height + rg_padding
        else:
            actual_sub_height = sub_height
        
        # Actualizar la altura del contenedor de subscription
        for group in group_info:
            if group['id'] == sub_group_id:
                group['height'] = actual_sub_height
                break
        
        current_y += actual_sub_height + 50  # Espacio entre subscriptions

    print(f"✅ Layout de red completado: {len(node_positions)} recursos posicionados")
    return node_positions, group_info, resource_to_parent_id

def generate_drawio_file(items, dependencies, embed_data=True, include_ids=None, diagram_mode='infrastructure', no_hierarchy_edges=False):
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
    elif diagram_mode == 'network':
        if no_hierarchy_edges:
            # En modo network con enlaces de RG deshabilitados, excluir solo enlaces RG → recursos
            print(f"🔗 Excluyendo TODOS los enlaces que involucren Resource Groups y enlaces VNet-Subnet")
            for src_id, tgt_id in dependencies:
                # Buscar los items correspondientes para determinar sus tipos
                source_item = None
                target_item = None
                for item in items:
                    if item['id'].lower() == src_id.lower():
                        source_item = item
                        break
                for item in items:
                    if item['id'].lower() == tgt_id.lower():
                        target_item = item
                        break
                
                if source_item and target_item:
                    source_type = source_item.get('type', '').lower()
                    target_type = target_item.get('type', '').lower()
                    
                    # Excluir CUALQUIER enlace que tenga un Resource Group como origen o destino
                    has_rg_involvement = (
                        source_type == 'microsoft.resources/subscriptions/resourcegroups' or 
                        target_type == 'microsoft.resources/subscriptions/resourcegroups'
                    )
                    
                    # Excluir enlaces entre VNets y Subnets
                    is_vnet_subnet_link = (
                        (source_type == 'microsoft.network/virtualnetworks' and 
                         target_type == 'microsoft.network/virtualnetworks/subnets') or
                        (source_type == 'microsoft.network/virtualnetworks/subnets' and 
                         target_type == 'microsoft.network/virtualnetworks')
                    )
                    
                    # Incluir todos los enlaces EXCEPTO aquellos que involucren Resource Groups o VNet-Subnet
                    if not has_rg_involvement and not is_vnet_subnet_link:
                        edges_to_create.append((src_id, tgt_id))
        else:
            # En modo network sin restricciones, agregar todas las dependencias
            print(f"🔗 Agregando {len(dependencies)} dependencias de red")
            edges_to_create.extend(dependencies)
    
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

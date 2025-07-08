"""
Funciones para generar el XML de draw.io y gestionar la disposición visual.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import json

# --- CATALOGACIÓN DE RECURSOS HIDDEN ---
# Recursos que se consideran "hidden" y requieren un estilo especial
HIDDEN_RESOURCE_TYPES = {
    "microsoft.network/privatednszones/virtualnetworklinks",
    # Aquí se pueden agregar más tipos de recursos hidden en el futuro
}

# Estilo especial para recursos hidden
HIDDEN_RESOURCE_STYLE = "verticalLabelPosition=bottom;verticalAlign=top;html=1;shape=mxgraph.infographic.shadedCube;isoAngle=15;fillColor=#10739E;strokeColor=none;aspect=fixed;"

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
    "microsoft.network/privatednszones/virtualnetworklinks": "img/lib/azure2/networking/Virtual_Network_Link.svg",
    "microsoft.recoveryservices/vaults": "img/lib/azure2/management_governance/Recovery_Services_Vaults.svg",
    "microsoft.resources/deploymentscripts": "img/lib/azure2/general/Deployment_Scripts.svg",
    "microsoft.resources/resources": "img/lib/azure2/general/Resources.svg",
    "microsoft.resources/subscriptions": "img/lib/azure2/general/Subscriptions.svg",
    "microsoft.resources/subscriptions/resourcegroups": "img/lib/azure2/general/Resource_Groups.svg",
    "microsoft.search/searchservices": "img/lib/azure2/app_services/Search_Services.svg",
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
    "microsoft.web/sites": "img/lib/azure2/compute/App_Services.svg",    
    "microsoft.databricks/accessconnectors": "data:image/png,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0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwdc80lHYo7BgJkAAJFCNg6p5pKPY8tiYBEiCB0hIwda/V0Gg0TivtCNgxEiABEugRAWhdo9EQ/IMGzty20Wgc3TQ0Go0LZgx8QwIkQAIDSgBa16J7R88Mc2pq6pAWw1UzBr4hARIggQEl0Gg0rmrqHjRwZpiTk5O7Nw2NRuO+GQPfkAAJkMCAEoDWNXUPGrjBMCcnJ3/aNDYajdENjPxAAiRAAgNEABrX1Dto30ZDm5qaOqflgls2uoBfkAAJkMCAEJicnLylqXfQvo2GtX79+ic1L8hfj9noIn5BAiRAAn1OoNFoHNOqddC+jkOanJx8e+uFjUZjeccL+SUJkAAJ9CGBRqOxrFXjoHmbHMbU1NTMVBINJycnV2+yAY0kQAIk0AcE1q9fv7pVDBuNxldm7Xa+dL67teHU1NRZIvKPszbmBSRAAiRQMgL333//YyYnJ89u1bRGo3G3uVRu7//k5ORzGo3GHW03mGo0Gh+8//77D7nvvvv+6d57731Uezt+JgESIIEHmwC0CRo1NTX1skajcWGj0YB2aUQKXicnJ++Axs2rn3/605+2bTQa17TeiO8fgEoWZMHfgb78HbhGRLqfzOVRLLfxh9+XP/yZ/yvy58ef3yL/Hbhtg2iUeU0PO1z817/+dd9Go3FGo9H42tTU1C+mpqYmFzlgik3LMoS/CxTcsvwOQJugUdAqaNbU1NQLO0gavyIBEiABEiABEiABEiCBORD4X9Mwl6EI3LQ7AAAAAElFTkSuQmCC;strokeWidth=1;imageBorder=none;clipPath=inset(15.88% 34.33% 44.9% 32.33%);",
    "microsoft.cdn/profiles": "img/lib/azure2/networking/CDN_Profiles.svg",
    "microsoft.cdn/profiles/afdendpoints": "img/lib/azure2/networking/CDN_Endpoints.svg",    
    "microsoft.insights/workbooks": "img/lib/azure2/analytics/Azure_Workbooks.svg",
    "microsoft.compute/diskencryptionsets": "img/lib/azure2/compute/Disk_Encryption_Sets.svg;"
    
}

FALLBACK_STYLES = {
    "managementgroup": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;shadow=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=14;",
    "subscription": "rounded=1;whiteSpace=wrap;html=1;shadow=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=12;",
    "resourcegroup": "image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image=img/lib/azure2/general/Resource_Groups.svg;",
    "resource": "rounded=1;whiteSpace=wrap;html=1;shadow=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
}

def get_node_style(resource_type):
    if not resource_type:
        return FALLBACK_STYLES['resource']
    
    resource_type_lower = resource_type.lower()
    
    # Verificar si es un recurso hidden
    if resource_type_lower in HIDDEN_RESOURCE_TYPES:
        print(f"🔒 Aplicando estilo hidden a recurso: {resource_type}")
        return HIDDEN_RESOURCE_STYLE
    
    # Obtener icono específico de Azure
    icon_path = AZURE_ICONS.get(resource_type_lower)
    if icon_path:
        return f"image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image={icon_path}"
    
    # Estilos especiales para tipos de contenedores
    if resource_type_lower == 'microsoft.management/managementgroups': 
        return FALLBACK_STYLES['managementgroup']
    if resource_type_lower == 'microsoft.resources/subscriptions': 
        return FALLBACK_STYLES['subscription']
    if resource_type_lower == 'microsoft.resources/subscriptions/resourcegroups': 
        return FALLBACK_STYLES['resourcegroup']
    
    # Estilo genérico para recursos sin icono específico
    return FALLBACK_STYLES['resource']
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
    """Disposición para diagrama de red - arquitectura de red realista estilo Azure con layout optimizado"""
    node_positions = {}
    group_info = []
    resource_to_parent_id = {}
    
    # Crear grafo de dependencias para optimizar layout
    dependency_graph = {}
    for src_id, tgt_id in dependencies:
        src_id_norm = src_id.lower()
        tgt_id_norm = tgt_id.lower()
        if src_id_norm not in dependency_graph:
            dependency_graph[src_id_norm] = set()
        if tgt_id_norm not in dependency_graph:
            dependency_graph[tgt_id_norm] = set()
        dependency_graph[src_id_norm].add(tgt_id_norm)
        dependency_graph[tgt_id_norm].add(src_id_norm)  # Bidireccional para agrupación

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
    
    def group_connected_resources(resources_list, dependency_graph):
        """Agrupa recursos conectados para minimizar cruces de líneas"""
        if not resources_list:
            return resources_list
            
        visited = set()
        groups = []
        
        # Crear grupos de recursos conectados
        for res_idx, res_item in resources_list:
            res_id = res_item['id'].lower()
            if res_id in visited:
                continue
                
            # BFS para encontrar recursos conectados
            group = []
            queue = [res_id]
            group_visited = set()
            
            while queue:
                current_id = queue.pop(0)
                if current_id in group_visited:
                    continue
                    
                group_visited.add(current_id)
                visited.add(current_id)
                
                # Encontrar el recurso correspondiente
                for r_idx, r_item in resources_list:
                    if r_item['id'].lower() == current_id:
                        group.append((r_idx, r_item))
                        break
                
                # Agregar recursos conectados
                if current_id in dependency_graph:
                    for connected_id in dependency_graph[current_id]:
                        if connected_id not in group_visited:
                            # Verificar si el recurso conectado está en la lista actual
                            for r_idx, r_item in resources_list:
                                if r_item['id'].lower() == connected_id:
                                    queue.append(connected_id)
                                    break
            
            if group:
                groups.append(group)
        
        # Reorganizar: grupos más grandes primero para mejor aprovechamiento del espacio
        groups.sort(key=len, reverse=True)
        
        # Aplanar grupos manteniendo la agrupación
        result = []
        for group in groups:
            result.extend(group)
        
        return result
    
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
        max_rg_width = 900   # Ancho máximo por RG (aún más generoso)
        max_rg_height = 1200  # Altura máxima por RG (aún más generoso)
        
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
        
        # PRE-CALCULAR todas las dimensiones de RGs para distribución homogénea
        rg_dimensions = {}  # rg_id -> (width, height)
        
        for rg_id, rg_data in sub_data['resource_groups'].items():
            # Analizar recursos del RG para calcular layout interno (reutilizar lógica existente)
            vnet_resources = []
            subnet_resources_by_vnet = {}
            vnet_direct_resources = {}
            standalone_resources = []
            
            for res_idx, res_item in rg_data['resources']:
                res_type = res_item.get('type', '').lower()
                
                if res_type == 'microsoft.network/virtualnetworks':
                    vnet_resources.append((res_idx, res_item))
                    vnet_id = res_item['id'].lower()
                    subnet_resources_by_vnet[vnet_id] = []
                    vnet_direct_resources[vnet_id] = []
                elif res_type == 'microsoft.network/virtualnetworks/subnets':
                    subnet_id = res_item['id'].lower()
                    vnet_id = '/'.join(subnet_id.split('/')[:-2])
                    if vnet_id not in subnet_resources_by_vnet:
                        subnet_resources_by_vnet[vnet_id] = []
                    subnet_resources_by_vnet[vnet_id].append((res_idx, res_item))
                else:
                    # Verificar si está asociado a una subnet específica
                    associated_to_subnet = False
                    for subnet_id, subnet_res_list in subnet_resources.items():
                        if (res_idx, res_item) in subnet_res_list:
                            associated_to_subnet = True
                            break
                    
                    if not associated_to_subnet:
                        # Verificar si pertenece a alguna VNet del RG
                        assigned_to_vnet = False
                        resource_id = res_item['id'].lower()
                        
                        for vnet_idx, vnet_item in vnet_resources:
                            vnet_id = vnet_item['id'].lower()
                            vnet_name = vnet_item.get('name', '').lower()
                            
                            belongs_to_vnet = False
                            props = res_item.get('properties', {})
                            if isinstance(props, dict):
                                for prop_name, prop_value in props.items():
                                    if isinstance(prop_value, dict) and 'id' in prop_value:
                                        if vnet_id in prop_value['id'].lower():
                                            belongs_to_vnet = True
                                            break
                                    elif isinstance(prop_value, str) and vnet_id in prop_value.lower():
                                        belongs_to_vnet = True
                                        break
                            
                            if not belongs_to_vnet:
                                if vnet_name in resource_id or res_item.get('name', '').lower().startswith(vnet_name):
                                    belongs_to_vnet = True
                            
                            if not belongs_to_vnet and res_type in [
                                'microsoft.network/networksecuritygroups',
                                'microsoft.network/routetables',
                                'microsoft.network/publicipaddresses',
                                'microsoft.network/loadbalancers',
                                'microsoft.network/applicationgateways',
                                'microsoft.network/azurefirewalls'
                            ]:
                                belongs_to_vnet = True
                            
                            if belongs_to_vnet:
                                vnet_direct_resources[vnet_id].append((res_idx, res_item))
                                assigned_to_vnet = True
                                res_item['parent_vnet_id'] = vnet_id
                                break
                        
                        if not assigned_to_vnet:
                            standalone_resources.append((res_idx, res_item))
            
            # Calcular dimensiones dinámicas del RG basadas en contenido
            rg_min_width = 400
            rg_min_height = 300
            rg_content_height = 70  # Header space
            rg_content_width = rg_min_width
            
            # Calcular espacio para VNets
            vnet_height_total = 0
            if vnet_resources:
                for vnet_idx, vnet_item in vnet_resources:
                    vnet_id = vnet_item['id'].lower()
                    vnet_subnets = subnet_resources_by_vnet.get(vnet_id, [])
                    vnet_direct_res = vnet_direct_resources.get(vnet_id, [])
                    
                    subnets_height = len(vnet_subnets) * 220
                    
                    direct_resources_height = 0
                    if vnet_direct_res:
                        resources_per_row = 3
                        direct_rows = (len(vnet_direct_res) + resources_per_row - 1) // resources_per_row
                        direct_resources_height = direct_rows * 100 + 40
                    
                    vnet_height = 120 + subnets_height + direct_resources_height + 120
                    vnet_height_total += vnet_height + 80
                    
                    max_subnet_width_in_vnet = 0
                    for subnet_id in vnet_subnets:
                        subnet_resources_filtered = [(r_idx, r) for r_idx, r in rg_data['resources'] if r.get('subnet_id') == subnet_id]
                        resource_count = len(subnet_resources_filtered)
                        needed_subnet_width = max(400, 200 + resource_count * 120)
                        max_subnet_width_in_vnet = max(max_subnet_width_in_vnet, needed_subnet_width)
                    
                    if vnet_direct_res:
                        resources_per_row = 3
                        direct_resources_width = min(len(vnet_direct_res), resources_per_row) * 140 + 80
                        max_subnet_width_in_vnet = max(max_subnet_width_in_vnet, direct_resources_width)
                    
                    vnet_width_needed = max(600, max_subnet_width_in_vnet + 120)
                    rg_content_width = max(rg_content_width, vnet_width_needed + 80)
                
                rg_content_height += vnet_height_total
            
            # Calcular espacio para recursos standalone
            if standalone_resources:
                tentative_width = max(rg_min_width, min(len(standalone_resources) * 120 + 80, 700))
                resources_per_row = max(1, min(3, (tentative_width - 80) // 120))
                standalone_rows = (len(standalone_resources) + resources_per_row - 1) // resources_per_row
                standalone_height = standalone_rows * 100 + 80
                rg_content_height += standalone_height
                
                standalone_width = min(len(standalone_resources), resources_per_row) * 120 + 80
                rg_content_width = max(rg_content_width, standalone_width)
            
            if not vnet_resources and len(standalone_resources) <= 1:
                rg_content_height = max(rg_min_height, 300)
                rg_content_width = max(rg_min_width, 500)
            
            rg_final_width = max(rg_min_width, min(rg_content_width, 900))
            rg_final_height = max(rg_min_height, min(rg_content_height, 1200))
            
            rg_dimensions[rg_id] = (rg_final_width, rg_final_height)
        
        # DISTRIBUCIÓN HOMOGÉNEA de RGs en grid uniforme
        rg_counter = 0
        current_row_y = 60 + rg_padding  # Posición Y base para la primera fila
        row_max_heights = []  # Alturas máximas por fila
        
        # Agrupar RGs por filas y calcular altura máxima por fila
        rg_items = list(sub_data['resource_groups'].items())
        for row_idx in range(rg_rows):
            row_start = row_idx * rgs_per_row
            row_end = min(row_start + rgs_per_row, len(rg_items))
            row_rgs = rg_items[row_start:row_end]
            
            # Calcular altura máxima de esta fila
            row_max_height = max([rg_dimensions[rg_id][1] for rg_id, _ in row_rgs])
            row_max_heights.append(row_max_height)
        
        for rg_id, rg_data in sub_data['resource_groups'].items():
            rg_row = rg_counter // rgs_per_row
            rg_col = rg_counter % rgs_per_row
            
            # Calcular posición Y basada en las alturas máximas de filas anteriores
            if rg_row == 0:
                rg_y = current_row_y
            else:
                rg_y = current_row_y + sum(row_max_heights[:rg_row]) + (rg_row * rg_padding)
            
            # Distribución homogénea en X: centrar RGs en el ancho disponible de la subscription
            available_width = sub_width - (2 * rg_padding)  # Ancho disponible dentro de la subscription
            rgs_in_this_row = min(rgs_per_row, len(sub_data['resource_groups']) - (rg_row * rgs_per_row))
            
            # Calcular ancho total necesario para esta fila basado en RGs reales
            row_start = rg_row * rgs_per_row
            row_end = min(row_start + rgs_per_row, len(rg_items))
            row_rgs = rg_items[row_start:row_end]
            total_rg_widths = sum([rg_dimensions[rg_id_in_row][0] for rg_id_in_row, _ in row_rgs])
            
            # Espaciado entre RGs en esta fila
            if rgs_in_this_row > 1:
                spacing_between_rgs = (available_width - total_rg_widths) / (rgs_in_this_row - 1)
                spacing_between_rgs = max(50, min(spacing_between_rgs, 150))  # Entre 50px y 150px
            else:
                spacing_between_rgs = 0
            
            # Calcular posición X para centrar la fila completa
            row_total_width = total_rg_widths + ((rgs_in_this_row - 1) * spacing_between_rgs)
            row_start_x = (available_width - row_total_width) / 2 + rg_padding
            
            # Posición X de este RG específico
            x_offset = 0
            for i in range(rg_col):
                prev_rg_id = rg_items[rg_row * rgs_per_row + i][0]
                x_offset += rg_dimensions[prev_rg_id][0] + spacing_between_rgs
            
            rg_x = row_start_x + x_offset
            
            rg_group_id = f"group_rg_{global_rg_counter}"
            global_rg_counter += 1
            
            # Obtener dimensiones precalculadas
            rg_final_width, rg_final_height = rg_dimensions[rg_id]
            
            # Reutilizar el análisis de recursos hecho en el precálculo
            vnet_resources = []
            subnet_resources_by_vnet = {}
            vnet_direct_resources = {}
            standalone_resources = []
            
            for res_idx, res_item in rg_data['resources']:
                res_type = res_item.get('type', '').lower()
                
                if res_type == 'microsoft.network/virtualnetworks':
                    vnet_resources.append((res_idx, res_item))
                    vnet_id = res_item['id'].lower()
                    subnet_resources_by_vnet[vnet_id] = []
                    vnet_direct_resources[vnet_id] = []
                elif res_type == 'microsoft.network/virtualnetworks/subnets':
                    subnet_id = res_item['id'].lower()
                    vnet_id = '/'.join(subnet_id.split('/')[:-2])
                    if vnet_id not in subnet_resources_by_vnet:
                        subnet_resources_by_vnet[vnet_id] = []
                    subnet_resources_by_vnet[vnet_id].append((res_idx, res_item))
                else:
                    # Verificar si está asociado a una subnet específica
                    associated_to_subnet = False
                    for subnet_id, subnet_res_list in subnet_resources.items():
                        if (res_idx, res_item) in subnet_res_list:
                            associated_to_subnet = True
                            break
                    
                    if not associated_to_subnet:
                        # Verificar si pertenece a alguna VNet por heurísticas
                        assigned_to_vnet = False
                        resource_id = res_item['id'].lower()
                        
                        for vnet_idx, vnet_item in vnet_resources:
                            vnet_id = vnet_item['id'].lower()
                            vnet_name = vnet_item.get('name', '').lower()
                            
                            belongs_to_vnet = False
                            props = res_item.get('properties', {})
                            if isinstance(props, dict):
                                for prop_name, prop_value in props.items():
                                    if isinstance(prop_value, dict) and 'id' in prop_value:
                                        if vnet_id in prop_value['id'].lower():
                                            belongs_to_vnet = True
                                            break
                                    elif isinstance(prop_value, str) and vnet_id in prop_value.lower():
                                        belongs_to_vnet = True
                                        break
                            
                            if not belongs_to_vnet:
                                if vnet_name in resource_id or res_item.get('name', '').lower().startswith(vnet_name):
                                    belongs_to_vnet = True
                            
                            if not belongs_to_vnet and res_type in [
                                'microsoft.network/networksecuritygroups',
                                'microsoft.network/routetables',
                                'microsoft.network/publicipaddresses',
                                'microsoft.network/loadbalancers',
                                'microsoft.network/applicationgateways',
                                'microsoft.network/azurefirewalls'
                            ]:
                                belongs_to_vnet = True
                            
                            if belongs_to_vnet:
                                vnet_direct_resources[vnet_id].append((res_idx, res_item))
                                assigned_to_vnet = True
                                res_item['parent_vnet_id'] = vnet_id
                                break
                        
                        if not assigned_to_vnet:
                            standalone_resources.append((res_idx, res_item))
            
            # Crear container de Resource Group con dimensiones precalculadas
            group_info.append({
                'id': rg_group_id,
                'parent_id': sub_group_id,
                'type': 'resource_group_container',
                'x': rg_x,
                'y': rg_y,
                'width': rg_final_width,
                'height': rg_final_height,
                'label': '',  # Sin label ya que el icono muestra el nombre
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
                vnet_direct_res = vnet_direct_resources.get(vnet_id, [])
                
                vnet_group_id = f"group_vnet_{global_vnet_counter}"
                global_vnet_counter += 1
                
                # Calcular dimensiones dinámicas de VNet con espaciado muy generoso
                subnet_count = len(vnet_subnets)
                direct_resource_count = len(vnet_direct_res)
                
                # Calcular ancho necesario basado en las subnets que contendrá
                max_subnet_width = 0
                for subnet_id in vnet_subnets:
                    subnet_resources_filtered = [(r_idx, r) for r_idx, r in rg_data['resources'] if r.get('subnet_id') == subnet_id]
                    resource_count = len(subnet_resources_filtered)
                    needed_subnet_width = max(400, 200 + resource_count * 120)
                    max_subnet_width = max(max_subnet_width, needed_subnet_width)
                
                # Considerar también el ancho para recursos directos de VNet
                direct_resources_width = 0
                if vnet_direct_res:
                    resources_per_row = 3
                    direct_resources_width = min(direct_resource_count, resources_per_row) * 140 + 80  # 140px por recurso + padding
                
                # VNet debe ser al menos 120px más ancha que el contenido más grande
                content_width = max(max_subnet_width, direct_resources_width)
                vnet_width = max(600, content_width + 120)
                
                # Calcular altura: header + subnets + recursos directos + padding MUY GENEROSO
                subnets_height = subnet_count * 220
                direct_resources_height = 0
                if vnet_direct_res:
                    resources_per_row = 3
                    direct_rows = (direct_resource_count + resources_per_row - 1) // resources_per_row
                    direct_resources_height = direct_rows * 100 + 80  # 100px por fila + padding extra entre secciones
                
                # VNet height con padding muy generoso para asegurar que todos los recursos quepan
                vnet_height = max(250, 120 + subnets_height + direct_resources_height + 120)  # Padding final muy generoso
                
                # Crear container de VNet
                group_info.append({
                    'id': vnet_group_id,
                    'parent_id': rg_group_id,
                    'type': 'vnet_container',
                    'x': 40,  # Aumentado de 20 a 40px para evitar solapamiento con el icono del RG
                    'y': current_rg_y,
                    'width': vnet_width,
                    'height': vnet_height,
                    'label': '',  # Sin label ya que el icono muestra el nombre
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
                    
                    # Aplicar agrupación de recursos conectados dentro de la subnet
                    current_subnet_resources = group_connected_resources(current_subnet_resources, dependency_graph)
                    
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
                        'label': '',  # Sin label ya que el icono muestra el nombre
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
                        
                        x_pos = resource_x + col * 180  # Espaciado horizontal aumentado para evitar solapamiento de nombres
                        y_pos = resource_y + row * 80   # Espaciado vertical aún más generoso
                        
                        node_positions[res_idx] = (x_pos, y_pos)
                        resource_to_parent_id[res_idx] = subnet_group_id
                    
                    subnet_y += subnet_height + 40  # Espaciado muy generoso entre subnets
                
                # 6. RECURSOS DIRECTOS DE LA VNet (después de todas las subnets)
                if vnet_direct_res:
                    print(f"🔗 Posicionando {len(vnet_direct_res)} recursos directos en VNet {vnet_item.get('name', 'N/A')}")
                    
                    # Aplicar agrupación de recursos conectados
                    vnet_direct_res = group_connected_resources(vnet_direct_res, dependency_graph)
                    
                    # Posición Y después de todas las subnets + separación
                    vnet_direct_y = subnet_y + 20  # Separación desde la última subnet
                    vnet_direct_x = 60  # Margen desde el borde izquierdo de la VNet
                    
                    resources_per_row = 3  # Máximo 3 recursos por fila
                    resource_counter = 0
                    
                    for res_idx, res_item in vnet_direct_res:
                        col = resource_counter % resources_per_row
                        row = resource_counter // resources_per_row
                        
                        x_pos = vnet_direct_x + col * 140  # Espaciado horizontal de 140px
                        y_pos = vnet_direct_y + row * 100  # Espaciado vertical de 100px
                        
                        node_positions[res_idx] = (x_pos, y_pos)
                        resource_to_parent_id[res_idx] = vnet_group_id  # Pertenecen directamente a la VNet
                        resource_counter += 1
                
                current_rg_y += vnet_height + 60  # Espaciado muy generoso entre VNets y recursos standalone
            
            # 6. RECURSOS NO VINCULADOS directamente en el RG (con mejor espaciado y agrupación)
            if standalone_resources:
                # Aplicar agrupación de recursos conectados para minimizar cruces
                standalone_resources = group_connected_resources(standalone_resources, dependency_graph)
                
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
            
            # Incrementar contador de RG
            rg_counter += 1
        
        # Calcular la altura real de la subscription basada en el contenido
        if row_max_heights:
            # Altura total = header + padding + suma de alturas máximas de filas + espacios entre filas + padding final
            total_rows_height = sum(row_max_heights) + ((len(row_max_heights) - 1) * rg_padding) if len(row_max_heights) > 1 else sum(row_max_heights)
            actual_sub_height = 60 + rg_padding + total_rows_height + rg_padding
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

def generate_drawio_multipage_file(items, dependencies, embed_data=True, include_ids=None, no_hierarchy_edges=False):
    """
    Genera un archivo draw.io con múltiples páginas, cada una con un tipo de diagrama diferente.
    
    Args:
        items: Lista de recursos de Azure
        dependencies: Lista de dependencias entre recursos
        embed_data: Si incrustar datos completos o solo el tipo
        include_ids: IDs específicos a incluir
        no_hierarchy_edges: Si aplicar filtrado de enlaces jerárquicos (solo para página Network)
    
    Returns:
        str: Contenido XML del archivo draw.io con múltiples páginas
    """
    import sys
    import json
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    
    print("INFO: Generando archivo draw.io con múltiples páginas...")
    
    # Crear el elemento raíz del archivo draw.io
    mxfile = ET.Element("mxfile", host="app.diagrams.net", agent="python-script")
    
    # Definir las páginas a generar
    pages = [
        {
            'id': 'infrastructure-page',
            'name': 'Infrastructure',
            'mode': 'infrastructure',
            'description': 'Jerarquía completa de Azure'
        },
        {
            'id': 'components-page', 
            'name': 'Components',
            'mode': 'components',
            'description': 'Agrupado por función y tipo'
        },
        {
            'id': 'network-page',
            'name': 'Network',
            'mode': 'network', 
            'description': 'Recursos de red con enlaces jerárquicos'
        },
        {
            'id': 'network-clean-page',
            'name': 'Network (Clean)',
            'mode': 'network',
            'description': 'Recursos de red sin enlaces jerárquicos',
            'no_hierarchy_edges': True
        }
    ]
    
    # Generar cada página
    for page_info in pages:
        print(f"📄 Generando página: {page_info['name']}")
        
        # Crear el elemento diagram para esta página
        diagram = ET.SubElement(mxfile, "diagram", 
                               id=page_info['id'], 
                               name=page_info['name'])
        
        # Crear el modelo de gráfico
        mxGraphModel = ET.SubElement(diagram, "mxGraphModel", 
                                   dx="2500", dy="2000", grid="1", gridSize="10", 
                                   guides="1", tooltips="1", connect="1", arrows="1", 
                                   fold="1", page="1", pageScale="1", 
                                   pageWidth="4681", pageHeight="3300")
        
        root = ET.SubElement(mxGraphModel, "root")
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")
        
        # Generar el layout específico para esta página
        azure_id_to_cell_id = {}
        levels = {0: [], 1: [], 2: [], 3: []}
        mg_id_to_idx, sub_id_to_idx, rg_id_to_idx = {}, {}, {}
        
        for i, item in enumerate(items):
            t = (item.get('type') or '').lower()
            if t == 'microsoft.management/managementgroups': 
                levels[0].append((i, item))
                mg_id_to_idx[item['id'].lower()] = i
            elif t == 'microsoft.resources/subscriptions': 
                levels[1].append((i, item))
                sub_id_to_idx[item['id'].lower()] = i
            elif t == 'microsoft.resources/subscriptions/resourcegroups': 
                levels[2].append((i, item))
                rg_id_to_idx[item['id'].lower()] = i
            else: 
                levels[3].append((i, item))
        
        node_positions, group_info, resource_to_parent_id = {}, [], {}
        tree_edges = []
        
        # Aplicar filtrado de enlaces jerárquicos si está configurado para esta página
        use_no_hierarchy_edges = page_info.get('no_hierarchy_edges', False)
        
        # Generar layout según el modo
        if page_info['mode'] == 'network':
            node_positions, group_info, resource_to_parent_id = generate_network_layout(
                items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
        elif page_info['mode'] == 'components':
            node_positions = generate_components_layout(
                items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
        else:  # 'infrastructure'
            node_positions, group_info, resource_to_parent_id, tree_edges = generate_infrastructure_layout(
                items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
        
        # Fallback de posicionamiento para nodos sin posición
        for i, item in enumerate(items):
            if i not in node_positions:
                node_positions[i] = ((i % 15) * 180, 1500 + (i // 15) * 150)
        
        # Crear agrupadores (contenedores)
        for group in group_info:
            group_cell = ET.SubElement(root, "mxCell", 
                                     id=group['id'], 
                                     style=group['style'], 
                                     parent=group.get('parent_id', '1'), 
                                     vertex="1")
            ET.SubElement(group_cell, "mxGeometry", 
                         attrib={'x': str(group['x']), 'y': str(group['y']), 
                                'width': str(group['width']), 'height': str(group['height']), 
                                'as': 'geometry'})
            ET.SubElement(group_cell, "object", 
                         attrib={'label': group['label'], 'as': 'value'})
        
        # Crear nodos de recursos
        for i, item in enumerate(items):
            cell_id = f"node-{i}"
            azure_id_to_cell_id[item['id'].lower()] = cell_id
            style = get_node_style(item.get('type'))
            
            # En modo network, ajustar estilo para RG, VNet y Subnet
            if page_info['mode'] == 'network':
                resource_type_lower = (item.get('type') or '').lower()
                if resource_type_lower in ['microsoft.resources/subscriptions/resourcegroups', 
                                         'microsoft.network/virtualnetworks', 
                                         'microsoft.network/virtualnetworks/subnets']:
                    if 'image=' in style:
                        style = style.replace('align=center', 'align=left;labelPosition=right;verticalLabelPosition=middle;verticalAlign=middle')
            
            parent_id = resource_to_parent_id.get(i, '1')
            
            node_cell = ET.SubElement(root, "mxCell", 
                                    id=cell_id, 
                                    style=style, 
                                    parent=parent_id, 
                                    vertex="1")
            
            x_pos, y_pos = node_positions.get(i)
            width, height = ('60', '60') if parent_id != '1' else ('80', '80')
            
            ET.SubElement(node_cell, "mxGeometry", 
                         attrib={'x': str(x_pos), 'y': str(y_pos), 
                                'width': width, 'height': height, 'as': 'geometry'})
            
            object_attribs = {'label': f"<b>{item.get('name', 'N/A')}</b>", 
                             'as': 'value', 'type': str(item.get('type', ''))}
            if embed_data:
                for key, value in item.items():
                    if key not in ['type', 'name']:
                        object_attribs[key.replace(':', '_')] = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            ET.SubElement(node_cell, "object", attrib=object_attribs)
        
        # Crear dependencias (flechas) según el modo de la página
        edges_to_create = []
        
        if page_info['mode'] == 'infrastructure' and tree_edges:
            # Usar conexiones del árbol jerárquico
            print(f"🔗 Página {page_info['name']}: Usando {len(tree_edges)} conexiones de árbol jerárquico")
            item_id_to_idx = {item['id'].lower(): i for i, item in enumerate(items)}
            
            for child_id, parent_id in tree_edges:
                if child_id in item_id_to_idx and parent_id in item_id_to_idx:
                    edges_to_create.append((child_id, parent_id))
        else:
            # Para otros modos, determinar dependencias según las opciones
            if page_info['mode'] == 'network' and use_no_hierarchy_edges:
                print(f"🔗 Página {page_info['name']}: Filtrando enlaces jerárquicos de {len(dependencies)} dependencias")
                
                # Crear diccionario de mapeo ID → tipo
                id_to_type = {item['id'].lower(): item.get('type', '').lower() for item in items}
                
                for src_id, tgt_id in dependencies:
                    source_type = id_to_type.get(src_id.lower(), '')
                    target_type = id_to_type.get(tgt_id.lower(), '')
                    
                    if source_type and target_type:
                        # Excluir enlaces jerárquicos
                        has_rg_involvement = (
                            source_type == 'microsoft.resources/subscriptions/resourcegroups' or 
                            target_type == 'microsoft.resources/subscriptions/resourcegroups'
                        )
                        
                        is_vnet_subnet_link = (
                            (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/virtualnetworks/subnets') or
                            (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/virtualnetworks')
                        )
                        
                        network_hierarchy_patterns = [
                            (source_type == 'microsoft.network/privateendpoints' and target_type == 'microsoft.network/virtualnetworks'),
                            (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/privateendpoints'),
                            (source_type == 'microsoft.network/privateendpoints' and target_type == 'microsoft.network/virtualnetworks/subnets'),
                            (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/privateendpoints'),
                            (source_type == 'microsoft.network/networkinterfaces' and target_type == 'microsoft.network/virtualnetworks'),
                            (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/networkinterfaces'),
                            (source_type == 'microsoft.network/networkinterfaces' and target_type == 'microsoft.network/virtualnetworks/subnets'),
                            (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/networkinterfaces'),
                            (source_type == 'microsoft.network/privatednszones/virtualnetworklinks' and target_type == 'microsoft.network/virtualnetworks'),
                            (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/privatednszones/virtualnetworklinks'),
                        ]
                        
                        is_network_hierarchy_link = any(network_hierarchy_patterns)
                        
                        if not has_rg_involvement and not is_vnet_subnet_link and not is_network_hierarchy_link:
                            edges_to_create.append((src_id, tgt_id))
                
                print(f"🔗 Página {page_info['name']}: Conservando {len(edges_to_create)} enlaces de dependencias")
            else:
                # Usar dependencias originales
                edges_to_create = dependencies
        
        # Agregar dependencias no jerárquicas para modo infrastructure
        if page_info['mode'] == 'infrastructure':
            print(f"🔗 Página {page_info['name']}: Agregando {len(dependencies)} dependencias adicionales")
            hierarchical_pairs = set(tree_edges) if tree_edges else set()
            
            for src_id, tgt_id in dependencies:
                dependency_pair = (src_id.lower(), tgt_id.lower())
                reverse_pair = (tgt_id.lower(), src_id.lower())
                
                if dependency_pair not in hierarchical_pairs and reverse_pair not in hierarchical_pairs:
                    edges_to_create.append((src_id, tgt_id))
        
        # Crear las flechas
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
                
                if page_info['mode'] == 'infrastructure' and tree_edges:
                    is_hierarchical = (source_id_lower, target_id_lower) in [(c, p) for c, p in tree_edges]
                    
                    if is_hierarchical:
                        source_item = None
                        target_item = None
                        for item in items:
                            if item['id'].lower() == source_id_lower:
                                source_item = item
                            elif item['id'].lower() == target_id_lower:
                                target_item = item
                        
                        if target_item and source_item:
                            target_type = target_item.get('type', '').lower()
                            source_type = source_item.get('type', '').lower()
                            
                            is_rg_to_resource = (target_type == 'microsoft.resources/subscriptions/resourcegroups' and 
                                               source_type not in ['microsoft.management/managementgroups', 
                                                                 'microsoft.resources/subscriptions',
                                                                 'microsoft.resources/subscriptions/resourcegroups'])
                
                if is_hierarchical and is_rg_to_resource:
                    style = "edgeStyle=straight;rounded=0;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
                elif is_hierarchical:
                    style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
                else:
                    style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#757575;strokeWidth=1;dashed=1;"
                
                edge_cell = ET.SubElement(root, "mxCell", 
                                        id=f"edge-{edge_counter}", 
                                        style=style, 
                                        parent="1", 
                                        source=source_cell, 
                                        target=target_cell, 
                                        edge="1")
                ET.SubElement(edge_cell, "mxGeometry", attrib={'relative': '1', 'as': 'geometry'})
                edge_counter += 1
    
    print("✅ Archivo multipágina generado exitosamente")
    return pretty_print_xml(mxfile)

def generate_drawio_file(items, dependencies, embed_data=True, include_ids=None, diagram_mode='infrastructure', no_hierarchy_edges=False):
    """
    Función principal para generar archivos draw.io
    """
    # Si el modo es 'all', generar archivo multipágina
    if diagram_mode == 'all':
        return generate_drawio_multipage_file(items, dependencies, embed_data, include_ids, no_hierarchy_edges)
    
    # Para otros modos, usar la función original
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
        
        # En modo network, ajustar estilo para RG, VNet y Subnet para mostrar texto a la derecha
        if diagram_mode == 'network':
            resource_type_lower = (item.get('type') or '').lower()
            if resource_type_lower in ['microsoft.resources/subscriptions/resourcegroups', 
                                     'microsoft.network/virtualnetworks', 
                                     'microsoft.network/virtualnetworks/subnets']:
                # Cambiar estilo para mostrar texto a la derecha del icono
                if 'image=' in style:
                    style = style.replace('align=center', 'align=left;labelPosition=right;verticalLabelPosition=middle;verticalAlign=middle')
        
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
        # Para otros modos (components, network), determinar las dependencias según las opciones
        if diagram_mode == 'network' and no_hierarchy_edges:
            # En modo network con filtrado de enlaces jerárquicos
            print(f"🔗 Filtrando enlaces jerárquicos (Resource Groups y VNet-Subnet) de {len(dependencies)} dependencias")
            
            # Crear diccionario de mapeo ID → tipo una sola vez para eficiencia
            id_to_type = {item['id'].lower(): item.get('type', '').lower() for item in items}
            
            for src_id, tgt_id in dependencies:
                source_type = id_to_type.get(src_id.lower(), '')
                target_type = id_to_type.get(tgt_id.lower(), '')
                
                if source_type and target_type:
                    # Excluir enlaces jerárquicos de Resource Groups
                    has_rg_involvement = (
                        source_type == 'microsoft.resources/subscriptions/resourcegroups' or 
                        target_type == 'microsoft.resources/subscriptions/resourcegroups'
                    )
                    
                    # Excluir enlaces VNet-Subnet (jerárquicos)
                    is_vnet_subnet_link = (
                        (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/virtualnetworks/subnets') or
                        (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/virtualnetworks')
                    )
                    
                    # Excluir enlaces jerárquicos específicos de recursos de red con VNets/Subnets
                    network_hierarchy_patterns = [
                        # Private Endpoints con VNets/Subnets
                        (source_type == 'microsoft.network/privateendpoints' and target_type == 'microsoft.network/virtualnetworks'),
                        (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/privateendpoints'),
                        (source_type == 'microsoft.network/privateendpoints' and target_type == 'microsoft.network/virtualnetworks/subnets'),
                        (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/privateendpoints'),
                        
                        # Network Interfaces con VNets/Subnets
                        (source_type == 'microsoft.network/networkinterfaces' and target_type == 'microsoft.network/virtualnetworks'),
                        (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/networkinterfaces'),
                        (source_type == 'microsoft.network/networkinterfaces' and target_type == 'microsoft.network/virtualnetworks/subnets'),
                        (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/networkinterfaces'),
                        
                        # Private DNS Zone Virtual Network Links con VNets (pero NO con Private DNS Zones)
                        (source_type == 'microsoft.network/privatednszones/virtualnetworklinks' and target_type == 'microsoft.network/virtualnetworks'),
                        (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/privatednszones/virtualnetworklinks'),
                    ]
                    
                    is_network_hierarchy_link = any(network_hierarchy_patterns)
                    
                    # Incluir el enlace si NO es jerárquico
                    if not has_rg_involvement and not is_vnet_subnet_link and not is_network_hierarchy_link:
                        edges_to_create.append((src_id, tgt_id))
            
            print(f"🔗 Conservando {len(edges_to_create)} enlaces de dependencias de red")
        else:
            # Para otros modos sin restricciones, usar las dependencias originales
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

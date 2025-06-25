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

def generate_drawio_file(items, dependencies, embed_data=True, include_ids=None):
    import sys
    import json
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    print("INFO: Generando el archivo .drawio con iconos y metadatos..." if embed_data else "INFO: Generando el archivo .drawio sin datos embebidos...")
    mxfile = ET.Element("mxfile", host="app.diagrams.net", agent="python-script")
    diagram = ET.SubElement(mxfile, "diagram", id="main-diagram", name="Azure Infrastructure")
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel", dx="2000", dy="1200", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="2339", pageHeight="1654")
    root = ET.SubElement(mxGraphModel, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    azure_id_to_cell_id = {}
    levels = {0: [], 1: [], 2: [], 3: []}
    mg_id_to_idx = {}
    sub_id_to_idx = {}
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
        else:
            levels[3].append((i, item))
    tree_children = {}
    tree_roots = set()
    rg_id_to_idx = {}
    for idx, item in levels[0]:
        mg_id = item['id'].lower()
        ancestors = item.get('properties', {}).get('details', {}).get('managementGroupAncestorsChain', [])
        parent = item.get('parent') or item.get('properties', {}).get('details', {}).get('parent', {}).get('id')
        parent_id = None
        if ancestors and isinstance(ancestors, list) and len(ancestors) > 0:
            parent_id = ancestors[0].get('id', '').lower()
        elif parent:
            parent_id = parent.lower()
        if parent_id and parent_id in mg_id_to_idx:
            tree_children.setdefault(parent_id, []).append(mg_id)
        else:
            tree_roots.add(mg_id)
    for idx, item in levels[1]:
        sub_id = item['id'].lower()
        mg_chain = item.get('properties', {}).get('managementGroupAncestorsChain')
        parent_id = None
        if isinstance(mg_chain, list) and len(mg_chain) > 0:
            mg_ancestor = mg_chain[0]
            parent_id = mg_ancestor.get('id') or (f"/providers/Microsoft.Management/managementGroups/{mg_ancestor.get('name')}")
            if parent_id: parent_id = parent_id.lower()
        if parent_id and parent_id in mg_id_to_idx:
            tree_children.setdefault(parent_id, []).append(sub_id)
        else:
            tree_roots.add(sub_id)
    for idx, item in levels[2]:
        rg_id = item['id'].lower()
        rg_id_to_idx[rg_id] = idx
        sub_id = f"/subscriptions/{item['subscriptionId']}".lower()
        if sub_id in sub_id_to_idx:
            tree_children.setdefault(sub_id, []).append(rg_id)
        else:
            tree_roots.add(rg_id)
    # --- Posicionar árbol recursivo (management group + sub-management groups + suscripciones + resource groups) como árbol vertical clásico ---
    y_step = 180
    x_step = 180
    node_positions = {}

    # Asegurar que los management groups hijos se distribuyen bajo sus padres (arbol real)
    def layout_tree_vertical(node_id, x, y):
        idx = mg_id_to_idx.get(node_id) or sub_id_to_idx.get(node_id) or rg_id_to_idx.get(node_id)
        children = tree_children.get(node_id, [])
        if not children:
            node_positions[idx] = (x, y)
            return x, x
        child_x = x
        child_centers = []
        for child in children:
            min_x, max_x = layout_tree_vertical(child, child_x, y + y_step)
            center = (min_x + max_x) // 2
            child_centers.append(center)
            child_x = max_x + x_step
        parent_x = (child_centers[0] + child_centers[-1]) // 2 if child_centers else x
        node_positions[idx] = (parent_x, y)
        min_x = min(child_centers) if child_centers else x
        max_x = max(child_centers) if child_centers else x
        return min_x, max_x

    next_x = 0
    for root_id in tree_roots:
        min_x, max_x = layout_tree_vertical(root_id, next_x, 0)
        next_x = max_x + x_step

    vnet_id_to_idx = {}
    subnet_id_to_idx = {}
    for idx, (i, item) in enumerate(levels[3]):
        t = (item.get('type') or '').lower()
        if t == 'microsoft.network/virtualnetworks':
            vnet_id_to_idx[item['id'].lower()] = i
        elif t == 'microsoft.network/virtualnetworks/subnets':
            subnet_id_to_idx[item['id'].lower()] = i
    vnet_children = {vnet_id: [] for vnet_id in vnet_id_to_idx}
    for subnet_id, idx in subnet_id_to_idx.items():
        subnet_item = items[idx]
        vnet_id = subnet_item.get('vnetId', '').lower()
        if vnet_id in vnet_children:
            vnet_children[vnet_id].append(subnet_id)
    vnet_y = 3 * y_step
    vnet_x = 0
    for vnet_id, vnet_idx in vnet_id_to_idx.items():
        subnets = vnet_children.get(vnet_id, [])
        if not subnets:
            node_positions[vnet_idx] = (vnet_x, vnet_y)
            vnet_x += x_step
        else:
            subnet_x = vnet_x
            subnet_centers = []
            for subnet_id in subnets:
                subnet_idx = subnet_id_to_idx[subnet_id]
                node_positions[subnet_idx] = (subnet_x, vnet_y + y_step)
                subnet_centers.append(subnet_x)
                subnet_x += x_step
            if subnet_centers:
                vnet_center = (subnet_centers[0] + subnet_centers[-1]) // 2
                node_positions[vnet_idx] = (vnet_center, vnet_y)
            vnet_x = subnet_x
    # --- Posicionar recursos hijos de resource group como árbol horizontal bajo su padre ---
    # Construir mapa de dependencias: recurso -> resource group
    rg_children = {rg_id: [] for rg_id in rg_id_to_idx}
    for idx, (i, item) in enumerate(levels[3]):
        parent_id = None
        # Buscar el resource group padre
        if 'resourceGroup' in item and 'subscriptionId' in item:
            parent_id = f"/subscriptions/{item['subscriptionId']}/resourcegroups/{item['resourceGroup']}".lower()
        if parent_id and parent_id in rg_children:
            rg_children[parent_id].append(i)
    # Para cada resource group, colocar sus recursos hijos en horizontal bajo el resource group
    for rg_id, rg_idx in rg_id_to_idx.items():
        children = rg_children.get(rg_id, [])
        if not children:
            continue
        rg_x, rg_y = node_positions[rg_idx]
        child_x = rg_x - (len(children)-1)*x_step//2
        for i in children:
            node_positions[i] = (child_x, rg_y + y_step)
            child_x += x_step
    # El resto de recursos (no hijos de resource group) en fila abajo
    placed_idxs = set()
    for children in rg_children.values():
        placed_idxs.update(children)
    resource_y = 3 * y_step + 2 * y_step
    resource_x = 0
    for idx, (i, item) in enumerate(levels[3]):
        if i in placed_idxs:
            continue
        node_positions[i] = (resource_x, resource_y)
        resource_x += x_step
    explore_link = 'data:action/json,{"title":"Explore","actions":[{"explore":{}}]}'
    include_ids_set = set(i.lower() for i in include_ids) if include_ids else None
    tenant_root_ids = set()
    if not include_ids_set:
        for item in items:
            if (item.get('type','').lower() == 'microsoft.management/managementgroups'):
                ancestors = item.get('properties', {}).get('details', {}).get('managementGroupAncestorsChain', [])
                parent = item.get('parent') or item.get('properties', {}).get('details', {}).get('parent', {}).get('id')
                if not ancestors and not parent:
                    tenant_root_ids.add(item['id'].lower())
    explore_link = 'data:action/json,{"title":"Explore","actions":[{"explore":{}}]}'
    explore_ids = set()
    if (not hasattr(sys, 'argv') or (not any('--include-ids' in arg or '--exclude-ids' in arg for arg in sys.argv))):
        for i, item in enumerate(items):
            t = (item.get('type') or '').lower()
            if t == 'microsoft.management/managementgroups':
                ancestors = item.get('properties', {}).get('details', {}).get('managementGroupAncestorsChain', [])
                parent = item.get('parent') or item.get('properties', {}).get('details', {}).get('parent', {}).get('id')
                if not ancestors and not parent:
                    explore_ids.add(item['id'].lower())
                    break
    else:
        ids = []
        if '--include-ids' in sys.argv:
            idx = sys.argv.index('--include-ids')
            ids = [arg for arg in sys.argv[idx+1:] if not arg.startswith('--')]
        for id_ in ids:
            explore_ids.add(id_.lower())
    for i, item in enumerate(items):
        cell_id = f"node-{i}"
        azure_id_to_cell_id[item['id'].lower()] = cell_id
        style = get_node_style(item.get('type'))
        node_cell = ET.SubElement(root, "mxCell", id=cell_id, style=style, parent="1", vertex="1")
        x_pos, y_pos = node_positions.get(i, ((i % 15) * 180, (i // 15) * 150))
        geometry_attribs = {'x': str(x_pos), 'y': str(y_pos), 'width': '80', 'height': '80', 'as': 'geometry'}
        ET.SubElement(node_cell, "mxGeometry", attrib=geometry_attribs)
        object_attribs = {'label': f"<b>{item.get('name', 'N/A')}</b>", 'as': 'value'}
        if 'type' in item:
            object_attribs['type'] = str(item['type'])
        if item['id'].lower() in explore_ids:
            object_attribs['link'] = explore_link
        if embed_data:
            for key, value in item.items():
                if key == 'type': continue
                attr_key = key.replace(':', '_')
                if value is not None:
                    object_attribs[attr_key] = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        ET.SubElement(node_cell, "object", attrib=object_attribs)
    for i, (source_id, target_id) in enumerate(dependencies):
        if source_id in azure_id_to_cell_id and target_id in azure_id_to_cell_id:
            edge_id = f"edge-{i}"
            source_cell, target_cell = azure_id_to_cell_id[source_id], azure_id_to_cell_id[target_id]
            edge_cell = ET.SubElement(root, "mxCell", id=edge_id, style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;", parent="1", source=source_cell, target=target_cell, edge="1")
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

import json
import subprocess
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
import os
import argparse

# --- CONFIGURACIÓN ---
# Nombre del archivo de salida. Puedes cambiarlo si lo deseas.
OUTPUT_FILENAME = "azure_full_hierarchy_with_icons.drawio"

# --- ICONOS Y ESTILOS DE AZURE PARA DRAW.IO ---
# Mapeo de tipos de recursos de Azure a sus iconos en la librería de Draw.io
AZURE_ICONS = {    
    "microsoft.management/managementgroups": "img/lib/azure2/general/Management_Group.svg",
    "microsoft.resources/subscriptions": "img/lib/azure2/general/Subscriptions.svg",
    "microsoft.resources/subscriptions/resourcegroups": "img/lib/azure2/general/Resource_Groups.svg",
    "microsoft.resources/deploymentscripts": "img/lib/azure2/general/Deployment_Script.svg",
    "microsoft.resources/resources": "img/lib/azure2/general/Resource.svg",
    "microsoft.compute/availabilitysets": "img/lib/azure2/compute/Availability_Set.svg",
    "microsoft.compute/restorepointcollections": "img/lib/azure2/compute/Restore_Points_Collections.svg",
    "microsoft.compute/virtualmachinescalesets": "img/lib/azure2/compute/Virtual_Machine_Scale_Set.svg",
    "microsoft.compute/virtualmachines/extensions": "img/lib/azure2/compute/Virtual_Machine_Extension.svg",    
    "microsoft.compute/virtualmachines": "img/lib/azure2/compute/Virtual_Machine.svg",
    "microsoft.network/virtualnetworks": "img/lib/azure2/networking/Virtual_Networks.svg",
    "microsoft.network/networkinterfaces": "img/lib/azure2/networking/Network_Interfaces.svg",
    "microsoft.network/publicipaddresses": "img/lib/azure2/networking/Public_IP_Address.svg",
    "microsoft.network/loadbalancers": "img/lib/azure2/networking/Load_Balancer.svg",
    "microsoft.network/applicationgateways": "img/lib/azure2/networking/Application_Gateway.svg",
    "microsoft.network/trafficmanagerprofiles": "img/lib/azure2/networking/Traffic_Manager_Profile.svg",
    "microsoft.network/expressroutecircuits": "img/lib/azure2/networking/ExpressRoute_Circuit.svg",
    "microsoft.network/networkwatchers": "img/lib/azure2/networking/Network_Watcher.svg",
    "microsoft.network/virtualnetworks/subnets": "img/lib/azure2/networking/Subnet.svg",
    "microsoft.network/virtualnetworkgateways/vpnconnections": "img/lib/azure2/networking/VPN_Connection.svg",
    "microsoft.network/routetables": "img/lib/azure2/networking/Route_Tables.svg",
    "microsoft.network/virtualnetworkgateways": "img/lib/azure2/networking/Virtual_Network_Gateway.svg",
    "microsoft.network/azurefirewalls": "img/lib/azure2/networking/Azure_Firewall.svg",
    "microsoft.network/azurefirewallpolicies": "img/lib/azure2/networking/Azure_Firewall_Policy.svg",
    "microsoft.network/dnszones": "img/lib/azure2/networking/DNS_Zone.svg",
    "microsoft.network/dnszones/recordsets": "img/lib/azure2/networking/DNS_Record_Set.svg",
    "microsoft.storage/storageaccounts/blobservices": "img/lib/azure2/storage/Blob_Service.svg",
    "microsoft.storage/storageaccounts/fileservices": "img/lib/azure2/storage/File_Service.svg",
    "microsoft.storage/storageaccounts/queueservices": "img/lib/azure2/storage/Queue_Service.svg",
    "microsoft.storage/storageaccounts/tableservices": "img/lib/azure2/storage/Table_Service.svg",
    "microsoft.storage/storageaccounts/blobservices/containers": "img/lib/azure2/storage/Blob_Container.svg",
    "microsoft.storage/storageaccounts/fileservices/shares": "img/lib/azure2/storage/File_Share.svg",
    "microsoft.storage/storageaccounts": "img/lib/azure2/storage/Storage_Account_Classic.svg",
    "microsoft.web/serverfarms": "img/lib/azure2/app_services/App_Service_Plan.svg",
    "microsoft.web/sites": "img/lib/azure2/app_services/App_Service.svg",
    "microsoft.sql/servers/databases": "img/lib/azure2/databases/SQL_Database.svg",
    "microsoft.sql/servers": "img/lib/azure2/databases/SQL_Server.svg",
    "microsoft.keyvault/vaults": "img/lib/azure2/security/Key_Vault.svg",
    "microsoft.insights/components": "img/lib/azure2/management_governance/Application_Insights.svg",
    "microsoft.automation/automationaccounts": "img/lib/azure2/management_governance/Automation_Accounts.svg",
    "microsoft.logic/workflows": "img/lib/azure2/app_services/Logic_App.svg",
    "microsoft.managedidentity/userassignedidentities": "img/lib/azure2/identity/Managed_Identities.svg",
    "microsoft.operationalinsights/workspaces": "img/lib/azure2/analytics/Log_Analytics_Workspaces.svg",
    "microsoft.operationsmanagement/solutions": "img/lib/mscae/Solutions.svg",
    "microsoft.network/networksecuritygroups": "img/lib/azure2/networking/Network_Security_Groups.svg",
    "microsoft.containerregistry/registries": "img/lib/azure2/containers/Container_Registry.svg",
    "microsoft.containerservice/managedclusters": "img/lib/azure2/containers/Kubernetes_Service.svg",
    "microsoft.servicebus/namespaces": "img/lib/azure2/messaging/Service_Bus.svg",
    "microsoft.eventgrid/topics": "img/lib/azure2/messaging/Event_Grid_Topics.svg",
    "microsoft.eventgrid/domains": "img/lib/azure2/messaging/Event_Grid_Domains.svg",
    "microsoft.eventgrid/eventsubscriptions": "img/lib/azure2/messaging/Event_Subscriptions.svg",
    "microsoft.cognitiveservices/accounts": "img/lib/azure2/ai_machine_learning/Cognitive_Services.svg",
    "microsoft.machinelearningservices/workspaces": "img/lib/azure2/ai_machine_learning/Machine_Learning.svg",
    "microsoft.apimanagement/service": "img/lib/azure2/app_services/API_Management.svg",
    "microsoft.search/searchservices": "img/lib/azure2/ai_machine_learning/Search.svg",
    "microsoft.recoveryservices/vaults": "img/lib/azure2/management_governance/Recovery_Services_Vaults.svg",
}


# Estilos de fallback si no se encuentra un icono
FALLBACK_STYLES = {
    "managementgroup": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;shadow=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=14;",
    "subscription": "rounded=1;whiteSpace=wrap;html=1;shadow=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=12;",
    "resourcegroup": "image;aspect=fixed;html=1;points=[];align=center;fontSize=12;image=img/lib/azure2/general/Resource_Groups.svg;",
    "resource": "rounded=1;whiteSpace=wrap;html=1;shadow=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
}

def get_node_style(resource_type):
    """Devuelve el estilo de draw.io apropiado, priorizando iconos."""
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


# --- CÓDIGO DEL SCRIPT ---

def pretty_print_xml(elem):
    """Formatea un elemento XML para que sea legible por humanos."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def get_azure_resources():
    """Obtiene la jerarquía completa de Azure usando una consulta de graph fiable y añade subnets como nodos hijos de los vnets."""
    print("INFO: Obteniendo la jerarquía completa de Azure con una consulta corregida...")
    if not os.system("az version > " + ("nul" if os.name == 'nt' else "/dev/null 2>&1")) == 0:
        print("\nERROR: Azure CLI no está instalado o no está en el PATH.")
        sys.exit(1)

    try:
        query = "resourcecontainers | union resources"
        command = ["az", "graph", "query", "-q", query, "--output", "json"]
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        resources = json.loads(result.stdout)
        items = resources['data']
        print(f"INFO: Se han encontrado {len(items)} elementos.")

        # --- Extraer subnets de cada VNet y agregarlas como recursos independientes ---
        extra_subnets = []
        for vnet in items:
            if vnet.get('type', '').lower() == 'microsoft.network/virtualnetworks':
                vnet_id = vnet['id']
                subnets = vnet.get('properties', {}).get('subnets', [])
                for subnet in subnets:
                    subnet_id = subnet.get('id')
                    if not subnet_id:
                        # Construir el id si no está
                        subnet_id = vnet_id + "/subnets/" + subnet.get('name', 'unknown')
                    subnet_item = {
                        'id': subnet_id,
                        'name': subnet.get('name', 'unknown'),
                        'type': 'microsoft.network/virtualnetworks/subnets',
                        'properties': subnet,
                        'vnetId': vnet_id
                    }
                    extra_subnets.append(subnet_item)
        if extra_subnets:
            print(f"INFO: Se han añadido {len(extra_subnets)} subnets como nodos independientes.")
        items.extend(extra_subnets)
        return items
    except Exception as e:
        print(f"\nERROR al ejecutar 'az graph query': {e}")
        print("Asegúrate de haber iniciado sesión ('az login') y tener los permisos necesarios.")
        sys.exit(1)

def find_dependencies(all_items):
    """Analiza los elementos para encontrar dependencias jerárquicas y de propiedades, vinculando correctamente recursos a subnets si corresponde."""
    print("INFO: Analizando dependencias...")
    dependencies = set()
    item_map = {item['id'].lower(): item for item in all_items}
    all_item_ids = set(item_map.keys())

    for item in all_items:
        source_id_lower = item['id'].lower()
        item_type_lower = item.get('type', '').lower()

        parent_id = None
        if item_type_lower == 'microsoft.management/managementgroups':
            try: parent_id = item['properties']['details']['parent']['id'].lower()
            except (KeyError, TypeError, AttributeError): parent_id = None
        elif item_type_lower == 'microsoft.resources/subscriptions':
            try: parent_id = item['properties']['managementGroup']['id'].lower()
            except (KeyError, TypeError): parent_id = None
        elif item_type_lower == 'microsoft.resources/subscriptions/resourcegroups':
            parent_id = f"/subscriptions/{item['subscriptionId']}".lower()
        elif 'resourceGroup' in item and 'subscriptionId' in item:
            parent_id = f"/subscriptions/{item['subscriptionId']}/resourcegroups/{item['resourceGroup']}".lower()
        elif item_type_lower == 'microsoft.network/virtualnetworks/subnets':
            parent_id = item.get('vnetId', '').lower()

        if parent_id and parent_id in all_item_ids:
            dependencies.add((source_id_lower, parent_id))

        # Dependencias por propiedades (entre recursos)
        def scan_properties(props):
            if isinstance(props, dict):
                for k, value in props.items():
                    # Si la clave o valor parece referenciar una subnet existente, priorizar esa dependencia
                    if isinstance(value, str) and '/subnets/' in value.lower():
                        subnet_id = value.lower()
                        if subnet_id in all_item_ids and subnet_id != source_id_lower:
                            dependencies.add((source_id_lower, subnet_id))
                            continue  # No seguir escaneando este valor, ya se vinculó a la subnet
                    scan_properties(value)
            elif isinstance(props, list):
                for element in props: scan_properties(element)
            elif isinstance(props, str):
                # Si es un id de subnet, priorizar esa dependencia
                if '/subnets/' in props.lower() and props.lower() in all_item_ids and props.lower() != source_id_lower:
                    dependencies.add((source_id_lower, props.lower()))
                elif props.lower() in all_item_ids and props.lower() != source_id_lower:
                    dependencies.add((source_id_lower, props.lower()))
        scan_properties(item.get('properties', {}))

    print(f"INFO: Se han encontrado {len(dependencies)} relaciones de dependencia.")
    return list(dependencies)


def generate_drawio_file(items, dependencies, embed_data=True):
    """Genera el archivo .drawio XML con datos incrustados como <object>."""
    print("INFO: Generando el archivo .drawio con iconos y metadatos...")
    mxfile = ET.Element("mxfile", host="app.diagrams.net", agent="python-script")
    diagram = ET.SubElement(mxfile, "diagram", id="main-diagram", name="Azure Infrastructure")
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel", dx="2000", dy="1200", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="2339", pageHeight="1654")
    root = ET.SubElement(mxGraphModel, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    azure_id_to_cell_id = {}
    
    # Primera pasada: Crear nodos
    for i, item in enumerate(items):
        cell_id = f"node-{i}"
        azure_id_to_cell_id[item['id'].lower()] = cell_id
        style = get_node_style(item.get('type'))
        
        node_cell = ET.SubElement(root, "mxCell", id=cell_id, style=style, parent="1", vertex="1")

        x_pos, y_pos = (i % 15) * 180, (i // 15) * 150
        geometry_attribs = {'x': str(x_pos), 'y': str(y_pos), 'width': '80', 'height': '80', 'as': 'geometry'}
        ET.SubElement(node_cell, "mxGeometry", attrib=geometry_attribs)
        
        object_attribs = {'label': f"<b>{item.get('name', 'N/A')}</b>", 'as': 'value'}
        if 'type' in item:
            object_attribs['type'] = str(item['type'])
        if embed_data:
            for key, value in item.items():
                if key == 'type': continue
                attr_key = key.replace(':', '_')
                if value is not None:
                    object_attribs[attr_key] = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        ET.SubElement(node_cell, "object", attrib=object_attribs)

    # Segunda pasada: Crear aristas
    for i, (source_id, target_id) in enumerate(dependencies):
        if source_id in azure_id_to_cell_id and target_id in azure_id_to_cell_id:
            edge_id = f"edge-{i}"
            source_cell, target_cell = azure_id_to_cell_id[source_id], azure_id_to_cell_id[target_id]
            edge_cell = ET.SubElement(root, "mxCell", id=edge_id, style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;", parent="1", source=source_cell, target=target_cell, edge="1")
            ET.SubElement(edge_cell, "mxGeometry", attrib={'relative': '1', 'as': 'geometry'})
            
    return pretty_print_xml(mxfile)

def filter_items_and_dependencies(items, dependencies, include_ids=None, exclude_ids=None):
    """Filtra los items y dependencias según los IDs a incluir o excluir (y sus descendientes)."""
    if not include_ids and not exclude_ids:
        return items, dependencies

    # Normalizar ids
    include_ids = set(i.lower() for i in include_ids) if include_ids else None
    exclude_ids = set(i.lower() for i in exclude_ids) if exclude_ids else set()

    # Construir mapa de hijos para recorrer descendientes
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
        # Incluir solo los seleccionados y sus descendientes
        selected_ids = collect_descendants(include_ids)
        selected_ids.update(include_ids)
    else:
        selected_ids = all_ids
    if exclude_ids:
        # Excluir los seleccionados y sus descendientes
        to_exclude = collect_descendants(exclude_ids)
        to_exclude.update(exclude_ids)
        selected_ids = selected_ids - to_exclude

    filtered_items = [item for item in items if item['id'].lower() in selected_ids]
    filtered_dependencies = [(src, tgt) for src, tgt in dependencies if src in selected_ids and tgt in selected_ids]
    return filtered_items, filtered_dependencies


def print_help_section():
    print("""
Opciones del script:
-------------------

Por defecto, el script genera el diagrama completo de la jerarquía de Azure.

Opciones disponibles:

  --no-embed-data
      No incrusta todos los datos en los nodos, solo el campo 'type'.
      Útil para reducir el tamaño del archivo .drawio.

  --include-ids <id1> <id2> ...
      Solo incluye en el diagrama los elementos (management group, suscripción, resource group) cuyos IDs se indiquen y todos sus descendientes.
      Ejemplo: --include-ids /providers/Microsoft.Management/managementGroups/miMG /subscriptions/xxxx-xxxx-xxxx

  --exclude-ids <id1> <id2> ...
      Excluye del diagrama los elementos (y sus descendientes) cuyos IDs se indiquen.
      Ejemplo: --exclude-ids /subscriptions/xxxx-xxxx-xxxx

  -h, --help
      Muestra esta ayuda y termina.

Notas:
- Los IDs deben ser los IDs completos de Azure (puedes obtenerlos con 'az account management-group list', 'az account list', etc.).
- Puedes combinar --include-ids y --exclude-ids para mayor control.
- El archivo generado se llama por defecto 'azure_full_hierarchy_with_icons.drawio'.

""")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de Diagramas de Jerarquía de Azure para Draw.io", add_help=False)
    parser.add_argument('--no-embed-data', action='store_true', help='No incrustar todos los datos, solo el campo type')
    parser.add_argument('--include-ids', nargs='+', help='IDs de management group, suscripción o resource group a incluir (y sus descendientes)')
    parser.add_argument('--exclude-ids', nargs='+', help='IDs de management group, suscripción o resource group a excluir (y sus descendientes)')
    parser.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda y termina')
    args = parser.parse_args()

    if args.help:
        print_help_section()
        sys.exit(0)

    print("--- Generador de Diagramas de Jerarquía de Azure para Draw.io ---")
    azure_items = get_azure_resources()
    
    if not azure_items:
        print("\nAVISO: No se encontraron elementos. Revisa tu login ('az login') y permisos.")
        sys.exit(0)
        
    dependencies = find_dependencies(azure_items)
    # Filtrar si corresponde
    azure_items, dependencies = filter_items_and_dependencies(
        azure_items, dependencies, include_ids=args.include_ids, exclude_ids=args.exclude_ids)
    drawio_content = generate_drawio_file(azure_items, dependencies, embed_data=not args.no_embed_data)
    
    try:
        with open(OUTPUT_FILENAME, "w", encoding='utf-8') as f:
            f.write(drawio_content)
        print(f"\n¡ÉXITO! Se ha creado el archivo '{OUTPUT_FILENAME}'.")
        print("\n--- PRÓXIMOS PASOS ---")
        print("1. Abre el archivo en https://app.diagrams.net.")
        print("2. Organiza el diagrama: Selecciona todo (Ctrl+A) -> Menú 'Organizar' -> 'Disposición' -> 'Gráfico Jerárquico'.")
        print("\n3. Selecciona cualquier icono y presiona Ctrl+M (Cmd+M en Mac) para ver todos sus datos.")
    except IOError as e:
        print(f"\nERROR al escribir el archivo: {e}")
        sys.exit(1)

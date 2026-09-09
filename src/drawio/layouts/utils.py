"""
Utilidades comunes para layouts de diagramas
"""


def normalize_azure_id(azure_id):
    """
    Normaliza un ID de Azure a lowercase para consistencia.
    
    Args:
        azure_id (str): ID de recurso de Azure
        
    Returns:
        str: ID normalizado
    """
    return azure_id.lower() if azure_id else ""


def generate_node_id(index):
    """
    Genera un ID único para un nodo basado en su índice.
    
    Args:
        index (int): Índice del nodo
        
    Returns:
        str: ID del nodo
    """
    return f"node-{index}"


def generate_group_id(group_type, counter):
    """
    Genera un ID único para un grupo/contenedor.
    
    Args:
        group_type (str): Tipo de grupo (rg, vnet, subnet, etc.)
        counter (int): Contador para evitar duplicados
        
    Returns:
        str: ID del grupo
    """
    return f"group_{group_type}_{counter}"


def generate_edge_id(source_id, target_id):
    """
    Genera un ID único para una conexión entre dos nodos.
    
    Args:
        source_id (str): ID del nodo origen
        target_id (str): ID del nodo destino
        
    Returns:
        str: ID de la conexión
    """
    return f"edge_{source_id}_{target_id}"


def extract_resource_name(azure_id):
    """
    Extrae el nombre del recurso de un ID de Azure.
    
    Args:
        azure_id (str): ID completo del recurso
        
    Returns:
        str: Nombre del recurso
    """
    if not azure_id:
        return "Unknown"
    
    # Los IDs de Azure tienen formato: /subscriptions/{sub}/resourceGroups/{rg}/providers/{provider}/{type}/{name}
    parts = azure_id.split('/')
    if len(parts) > 0:
        return parts[-1]  # El último elemento es el nombre
    
    return azure_id


def calculate_grid_layout(items_count, max_per_row=3, spacing_x=150, spacing_y=120, start_x=100, start_y=100):
    """
    Calcula posiciones en grid para una lista de elementos.
    
    Args:
        items_count (int): Número de elementos
        max_per_row (int): Máximo elementos por fila
        spacing_x (int): Espaciado horizontal
        spacing_y (int): Espaciado vertical
        start_x (int): Posición X inicial
        start_y (int): Posición Y inicial
        
    Returns:
        list: Lista de tuplas (x, y) con las posiciones
    """
    positions = []
    
    for i in range(items_count):
        row = i // max_per_row
        col = i % max_per_row
        
        x = start_x + col * spacing_x
        y = start_y + row * spacing_y
        
        positions.append((x, y))
    
    return positions


def calculate_container_size(child_positions, padding=60):
    """
    Calcula el tamaño necesario para un contenedor basado en las posiciones de sus hijos.
    
    Args:
        child_positions (list): Lista de tuplas (x, y) de posiciones de hijos
        padding (int): Padding alrededor del contenido
        
    Returns:
        tuple: (width, height) del contenedor
    """
    if not child_positions:
        return (200, 100)  # Tamaño mínimo
    
    min_x = min(pos[0] for pos in child_positions)
    max_x = max(pos[0] for pos in child_positions)
    min_y = min(pos[1] for pos in child_positions)
    max_y = max(pos[1] for pos in child_positions)
    
    # Asumir nodos de 120x80 para calcular el tamaño total
    node_width, node_height = 120, 80
    
    width = (max_x - min_x) + node_width + (2 * padding)
    height = (max_y - min_y) + node_height + (2 * padding)
    
    return (max(200, width), max(100, height))


def group_resources_by_type(items):
    """
    Agrupa recursos por su tipo de Azure.
    
    Args:
        items (list): Lista de recursos con 'type' 
        
    Returns:
        dict: Diccionario {tipo: [recursos]}
    """
    groups = {}
    
    for item in items:
        resource_type = (item.get('type') or '').lower()
        if resource_type not in groups:
            groups[resource_type] = []
        groups[resource_type].append(item)
    
    return groups


def classify_network_resource(resource_type):
    """
    Clasifica un recurso por su función en la arquitectura de red.
    
    Args:
        resource_type (str): Tipo de recurso de Azure
        
    Returns:
        str: Categoría ('edge', 'connectivity', 'security', 'compute', 'storage', 'other')
    """
    resource_type_lower = resource_type.lower()
    
    # Recursos de edge/frontera
    if any(edge_type in resource_type_lower for edge_type in [
        'applicationgateway', 'loadbalancer', 'publicip', 'trafficmanager'
    ]):
        return 'edge'
    
    # Recursos de conectividad
    if any(conn_type in resource_type_lower for conn_type in [
        'virtualnetworkgateway', 'expressroute', 'connection', 'vpn'
    ]):
        return 'connectivity'
    
    # Recursos de seguridad
    if any(sec_type in resource_type_lower for sec_type in [
        'firewall', 'networksecuritygroup', 'keyvault', 'security'
    ]):
        return 'security'
    
    # Recursos de compute
    if any(comp_type in resource_type_lower for comp_type in [
        'virtualmachine', 'containerservice', 'web/sites'
    ]):
        return 'compute'
    
    # Recursos de storage
    if 'storage' in resource_type_lower:
        return 'storage'
    
    return 'other'


def extract_subscription_from_id(azure_id):
    """
    Extrae el ID de suscripción de un ID de recurso de Azure.
    
    Args:
        azure_id (str): ID completo del recurso
        
    Returns:
        str: ID de la suscripción o None
    """
    if not azure_id:
        return None
    
    parts = azure_id.lower().split('/')
    try:
        if 'subscriptions' in parts:
            sub_index = parts.index('subscriptions')
            if sub_index + 1 < len(parts):
                return '/subscriptions/' + parts[sub_index + 1]
    except (ValueError, IndexError):
        pass
    
    return None


def extract_resource_group_from_id(azure_id):
    """
    Extrae el ID del resource group de un ID de recurso de Azure.
    
    Args:
        azure_id (str): ID completo del recurso
        
    Returns:
        str: ID del resource group o None
    """
    if not azure_id:
        return None
    
    parts = azure_id.lower().split('/')
    try:
        if 'resourcegroups' in parts:
            rg_index = parts.index('resourcegroups')
            if rg_index + 1 < len(parts):
                # Reconstruir el ID hasta el resource group
                sub_part = '/'.join(parts[:rg_index])
                rg_name = parts[rg_index + 1]
                return f"{sub_part}/resourcegroups/{rg_name}"
    except (ValueError, IndexError):
        pass
    
    return None


# Categorías funcionales usadas por los modos 'components' y 'hld'. Centralizadas
# aquí para que ambos layouts clasifiquen los recursos exactamente igual
# (evita reglas duplicadas y divergentes entre módulos).
COMPONENT_CATEGORIES = [
    'Compute', 'Storage', 'Network', 'Database', 'Analytics', 'IoT',
    'Security', 'AI/ML', 'Management', 'Media', 'Other'
]

GOVERNANCE_RESOURCE_TYPES = {
    'microsoft.management/managementgroups',
    'microsoft.resources/subscriptions',
    'microsoft.resources/subscriptions/resourcegroups',
}


def classify_component_category(resource_type):
    """
    Clasifica un recurso en una categoría funcional (bill of materials).

    Args:
        resource_type (str): Tipo de recurso de Azure (con o sin mayúsculas)

    Returns:
        str | None: Nombre de categoría (ver COMPONENT_CATEGORIES), o None si el
            recurso es de gobierno (Management Group/Subscription/Resource Group)
            y debe excluirse de estos diagramas.
    """
    resource_type_lower = (resource_type or '').lower()

    if resource_type_lower in GOVERNANCE_RESOURCE_TYPES:
        return None

    if any(t in resource_type_lower for t in [
        'compute/virtualmachines', 'web/sites', 'containerservice',
        'web/serverfarms', 'compute/availabilitysets', 'compute/virtualmachinescalesets',
        'batch/batchaccounts', 'app/managedenvironments', 'app/containerapps',
        'appplatform/', 'servicefabric/', 'desktopvirtualization/', 'compute/galleries',
        'redhatopenshift/'
    ]):
        return 'Compute'

    if any(t in resource_type_lower for t in [
        'storage/storageaccounts', 'compute/disks', 'compute/diskencryptionsets',
        'netapp/', 'storagecache/', 'databoxedge/', 'storagesync/'
    ]):
        return 'Storage'

    if 'network/' in resource_type_lower:
        return 'Network'

    if any(t in resource_type_lower for t in ['sql/', 'documentdb/', 'dbfor', 'cache/', 'search/']):
        return 'Database'

    if any(t in resource_type_lower for t in [
        'synapse/', 'datafactory/', 'eventhub/', 'purview/', 'kusto/',
        'streamanalytics/', 'hdinsight/', 'datalakeanalytics/', 'datalakestore/',
        'analysisservices/', 'powerbidedicated/', 'databricks/'
    ]):
        return 'Analytics'

    if any(t in resource_type_lower for t in [
        'devices/iothubs', 'devices/provisioningservices', 'digitaltwins/',
        'maps/', 'iotcentral/', 'timeseriesinsights/'
    ]):
        return 'IoT'

    if any(t in resource_type_lower for t in [
        'keyvault/', 'security/', 'managedidentity/', 'aad/', 'securityinsights/'
    ]):
        return 'Security'

    if any(t in resource_type_lower for t in [
        'cognitiveservices/', 'machinelearningservices/', 'botservice/'
    ]):
        return 'AI/ML'

    if any(t in resource_type_lower for t in [
        'insights/', 'operationalinsights/', 'automation/',
        'operationsmanagement/', 'recoveryservices/', 'blueprint/',
        'policyinsights/', 'hybridcompute/', 'consumption/', 'advisor/',
        'servicebus/', 'eventgrid/', 'logic/', 'apimanagement/'
    ]):
        return 'Management'

    if any(t in resource_type_lower for t in ['cdn/', 'media/']):
        return 'Media'

    return 'Other'

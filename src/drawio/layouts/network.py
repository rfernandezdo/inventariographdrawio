#!/usr/bin/env python3
"""
Layout de red jerárquico y sin colisiones para Azure.

Este módulo genera un layout de red que representa la jerarquía completa:
Subscription -> Resource Group -> VNet -> Subnet -> Recursos.

Utiliza un algoritmo de cálculo de tamaño dinámico y posicionamiento en grid
para aseg                'label': '', 'style': CONTAINER_STYLES['resource_group']rar que no haya solapamientos, incluso con RGs y VNets de tamaños muy diferentes.
"""

import math
from typing import List, Dict, Tuple, Any, Optional

# --- CONSTANTES DE LAYOUT ---
# Espaciados y márgenes para un layout limpio y legible
PADDING = {'top': 60, 'bottom': 60, 'left': 60, 'right': 60}
RG_GRID_SPACING = {'x': 100, 'y': 100}
VNET_SPACING = {'y': 80}
SUBNET_SPACING = {'y': 60}
RESOURCE_SPACING = {'x': 210, 'y': 150}
RESOURCES_PER_ROW = {'subnet': 2, 'vnet': 3, 'rg': 3}

# Dimensiones mínimas para contenedores
MIN_WIDTH = {'vnet': 600, 'subnet': 450}
MIN_HEIGHT = {'rg': 300, 'vnet': 250, 'subnet': 200}

# Estilos para los contenedores generados
CONTAINER_STYLES = {
"subscription": "container=1;rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=16;fontStyle=1;align=left;verticalAlign=top;spacingLeft=20;spacingTop=15;",
"resource_group": "container=1;rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#90A4AE;dashed=1;dashPattern=8 4;labelBackgroundColor=none;fontSize=14;fontStyle=1;align=left;verticalAlign=top;spacingLeft=15;spacingTop=15;",
"vnet": "container=1;rounded=0;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1976D2;fontSize=13;fontStyle=1;align=left;verticalAlign=top;spacingLeft=15;spacingTop=15;",
"subnet": "container=1;rounded=0;whiteSpace=wrap;html=1;fillColor=#ECEFF1;strokeColor=#546E7A;fontSize=12;fontStyle=0;align=left;verticalAlign=top;spacingLeft=15;spacingTop=15;",
"region": "container=0;rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#9575CD;dashed=1;dashPattern=12 6;fontSize=13;fontStyle=2;align=left;verticalAlign=top;spacingLeft=12;spacingTop=8;"
}

# Margen del rect\u00e1ngulo de regi\u00f3n alrededor de los Resource Groups que engloba
REGION_MARGIN = 30

def _get_parent_id(azure_id: str, level: str) -> Optional[str]:
    """Extrae el ID del padre de un ID de recurso de Azure."""
    parts = azure_id.lower().split('/')
    try:
        if level == 'sub' and 'subscriptions' in parts:
            idx = parts.index('subscriptions')
            return '/'.join(parts[:idx + 2])
        if level == 'rg' and 'resourcegroups' in parts:
            idx = parts.index('resourcegroups')
            return '/'.join(parts[:idx + 2])
        if level == 'vnet' and 'virtualnetworks' in parts:
            idx = parts.index('virtualnetworks')
            return '/'.join(parts[:idx + 2])
    except (ValueError, IndexError):
        return None
    return None

def _organize_resources_by_hierarchy(items: List[Dict]) -> Dict:
    """
    Organiza los recursos en una estructura jerárquica anidada:
    Subscription -> RG -> VNet -> Subnet -> Recursos.
    """
    subscriptions = {}
    item_map = {item['id'].lower(): item for item in items}
    
    # 1. Inicializar todas las entidades contenedoras (Subs, RGs, VNets, Subnets)
    for item in items:
        item_id = item['id'].lower()
        item_type = (item.get('type') or '').lower()

        if item_type == 'microsoft.resources/subscriptions':
            if item_id not in subscriptions:
                subscriptions[item_id] = {**item, 'resource_groups': {}}
        
        elif item_type == 'microsoft.resources/subscriptions/resourcegroups':
            sub_id = _get_parent_id(item_id, 'sub') # No implementado, pero como ejemplo
            # Esto requiere una función _get_parent_id más robusta o pasar el parent_id
            # Por ahora, asumimos una estructura plana de RGs por subscripción
            pass

    # 2. Crear estructura anidada
    # Esta parte es compleja y se simplifica en el layout principal
    # La lógica real de anidación se hace durante el cálculo del layout
    
    return subscriptions # Devuelve una estructura simplificada por ahora


def _find_subnet_for_resource(item: Dict, nic_to_subnet_map: Dict) -> Optional[str]:
    """
    Determina el ID de la subnet para un recurso, ya sea por asociación directa o indirecta.
    Para NSGs, retorna solo la primera subnet (usar _find_all_subnets_for_nsg para múltiples).
    """
    props = item.get('properties', {})
    item_type = (item.get('type') or '').lower()

    # 1. Asociación directa en propiedades
    if 'subnet' in props and isinstance(props['subnet'], dict) and props['subnet'].get('id'):
        return props['subnet']['id']
    
    if 'ipConfigurations' in props and props.get('ipConfigurations') and isinstance(props['ipConfigurations'], list):
        ip_config = props['ipConfigurations'][0]
        if 'properties' in ip_config and 'subnet' in ip_config.get('properties', {}) and ip_config['properties']['subnet'].get('id'):
            return ip_config['properties']['subnet']['id']

    # 2. Asociación para Network Security Groups (NSG) - solo primera subnet
    if item_type == 'microsoft.network/networksecuritygroups':
        if 'subnets' in props and isinstance(props.get('subnets'), list) and props['subnets']:
            # Tomar la primera subnet asociada 
            first_subnet = props['subnets'][0]
            if isinstance(first_subnet, dict) and 'id' in first_subnet:
                return first_subnet['id']

    # 3. Asociación indirecta (vía NIC para VMs, etc.)
    if 'networkProfile' in props and isinstance(props.get('networkProfile'), dict) and isinstance(props['networkProfile'].get('networkInterfaces'), list):
        for nic_ref in props['networkProfile']['networkInterfaces']:
            if isinstance(nic_ref, dict) and 'id' in nic_ref:
                nic_id = nic_ref['id'].lower()
                if nic_id in nic_to_subnet_map:
                    return nic_to_subnet_map[nic_id]

    # 4. Asociación para Private Endpoints (que tienen su propia NIC)
    if item_type == 'microsoft.network/privateendpoints':
        if 'networkInterfaces' in props and isinstance(props.get('networkInterfaces'), list) and props['networkInterfaces']:
            nic_id = props['networkInterfaces'][0].get('id', '').lower()
            if nic_id in nic_to_subnet_map:
                return nic_to_subnet_map[nic_id]

    # 5. Asociación para servicios con VNet integration (App Services, Functions)
    if 'virtualNetworkSubnetId' in props and props.get('virtualNetworkSubnetId'):
        return props['virtualNetworkSubnetId']

    return None


def _find_all_subnets_for_nsg(item: Dict) -> List[str]:
    """
    Encuentra todas las subnets asociadas a un NSG.
    """
    props = item.get('properties', {})
    item_type = (item.get('type') or '').lower()
    
    if item_type == 'microsoft.network/networksecuritygroups':
        if 'subnets' in props and isinstance(props.get('subnets'), list):
            subnet_ids = []
            for subnet_ref in props['subnets']:
                if isinstance(subnet_ref, dict) and 'id' in subnet_ref:
                    subnet_ids.append(subnet_ref['id'])
            return subnet_ids
    
    return []

def _find_all_subnets_for_route_table(item: Dict) -> List[str]:
    """
    Encuentra todas las subnets asociadas a una Route Table.
    """
    props = item.get('properties', {})
    item_type = (item.get('type') or '').lower()
    
    if item_type == 'microsoft.network/routetables':
        if 'subnets' in props and isinstance(props.get('subnets'), list):
            subnet_ids = []
            for subnet_ref in props['subnets']:
                if isinstance(subnet_ref, dict) and 'id' in subnet_ref:
                    subnet_ids.append(subnet_ref['id'])
            return subnet_ids
    
    return []

def generate_network_layout(items: List[Dict], dependencies: List[Dict], **kwargs) -> Tuple[List[Dict], Dict[int, Tuple[int, int]], List[Dict], Dict[int, str]]:
    """
    Genera un layout de red jerárquico y sin colisiones.
    """
    print("🚀 Iniciando layout de red jerárquico...")

    group_info = []
    node_positions = {}
    resource_to_parent_id = {}
    
    # Crear elementos virtuales para NSGs y Route Tables que aparecen en múltiples subnets
    extended_items = items.copy()
    nsg_virtual_instances = {}  # {original_index: [virtual_indexes]}
    rt_virtual_instances = {}   # {original_index: [virtual_indexes]}
    
    for i, item in enumerate(items):
        item_type = (item.get('type') or '').lower()
        
        # Procesar NSGs con múltiples subnets
        if item_type == 'microsoft.network/networksecuritygroups':
            subnet_ids = _find_all_subnets_for_nsg(item)
            if len(subnet_ids) > 1:
                # NSG con múltiples subnets - crear instancias virtuales para TODAS las subnets
                virtual_indexes = []
                for j, subnet_id in enumerate(subnet_ids):
                    # Crear instancias virtuales para todas las subnets (incluida la primera)
                    virtual_item = item.copy()
                    virtual_item['_virtual_subnet_id'] = subnet_id.lower()
                    virtual_item['_original_index'] = i
                    virtual_item['_is_assignment'] = True
                    
                    # Modificar el ID y nombre para que sean únicos
                    original_id = virtual_item['id']
                    original_name = virtual_item.get('name', '')
                    
                    virtual_item['id'] = f"{original_id}--assignment-{j}"
                    virtual_item['name'] = f"{original_name} (asignación)"
                    
                    virtual_index = len(extended_items)
                    extended_items.append(virtual_item)
                    virtual_indexes.append(virtual_index)
                    
                nsg_virtual_instances[i] = virtual_indexes
        
        # Procesar Route Tables con múltiples subnets
        elif item_type == 'microsoft.network/routetables':
            subnet_ids = _find_all_subnets_for_route_table(item)
            if len(subnet_ids) > 1:
                # Route Table con múltiples subnets - crear instancias virtuales para TODAS las subnets
                virtual_indexes = []
                for j, subnet_id in enumerate(subnet_ids):
                    # Crear instancias virtuales para todas las subnets
                    virtual_item = item.copy()
                    virtual_item['_virtual_subnet_id'] = subnet_id.lower()
                    virtual_item['_original_index'] = i
                    virtual_item['_is_assignment'] = True
                    
                    # Modificar el ID y nombre para que sean únicos
                    original_id = virtual_item['id']
                    original_name = virtual_item.get('name', '')
                    
                    virtual_item['id'] = f"{original_id}--assignment-{j}"
                    virtual_item['name'] = f"{original_name} (asignación)"
                    
                    virtual_index = len(extended_items)
                    extended_items.append(virtual_item)
                    virtual_indexes.append(virtual_index)
                    
                rt_virtual_instances[i] = virtual_indexes
    
    item_map = {item['id'].lower(): (i, item) for i, item in enumerate(extended_items)}
    
    # 1. Organizar recursos por jerarquía
    subs = {}
    # Pre-construir mapa de NICs a subnets para una búsqueda más rápida
    nic_to_subnet_map = {}
    for i, item in enumerate(extended_items):
        item_type = (item.get('type') or '').lower()
        if item_type == 'microsoft.network/networkinterfaces':
            props = item.get('properties', {})
            if 'ipConfigurations' in props and props.get('ipConfigurations'):
                ip_config = props['ipConfigurations'][0]
                if 'properties' in ip_config and 'subnet' in ip_config.get('properties', {}) and ip_config['properties']['subnet'].get('id'):
                    nic_to_subnet_map[item['id'].lower()] = ip_config['properties']['subnet']['id'].lower()

    for i, item in enumerate(extended_items):
        item_id = item['id'].lower()
        item_type = (item.get('type') or '').lower()
        
        # Inicializar contenedores (RG, VNet, Subnet)
        if 'resourcegroups' in item_id:
            rg_id = _get_parent_id(item_id, 'rg')
            sub_id = _get_parent_id(rg_id, 'sub') if rg_id else None
            if not sub_id:
                continue

            if sub_id not in subs:
                subs[sub_id] = {'resource_groups': {}}
            if rg_id not in subs[sub_id]['resource_groups']:
                subs[sub_id]['resource_groups'][rg_id] = {'vnets': {}, 'standalone_resources': []}

            if item_type == 'microsoft.resources/subscriptions/resourcegroups':
                subs[sub_id]['resource_groups'][rg_id]['item_index'] = i
            elif 'virtualnetworks' in item_id:
                vnet_id = _get_parent_id(item_id, 'vnet')
                if vnet_id not in subs[sub_id]['resource_groups'][rg_id]['vnets']:
                    subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id] = {'subnets': {}, 'direct_resources': []}
                
                if item_type == 'microsoft.network/virtualnetworks':
                    subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id]['item_index'] = i
                elif item_type == 'microsoft.network/virtualnetworks/subnets':
                    if item_id not in subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id]['subnets']:
                        subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id]['subnets'][item_id] = {'resources': []}
                    subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id]['subnets'][item_id]['item_index'] = i
    
    # Asociar todos los recursos a su contenedor correcto
    for i, item in enumerate(extended_items):
        item_id = item['id'].lower()
        item_type = (item.get('type') or '').lower()

        # Ignorar los contenedores mismos, ya están procesados
        if item_type in ['microsoft.resources/subscriptions', 'microsoft.resources/subscriptions/resourcegroups', 'microsoft.network/virtualnetworks', 'microsoft.network/virtualnetworks/subnets']:
            continue

        # Manejo especial para NSGs que pueden estar en múltiples subnets
        if item_type == 'microsoft.network/networksecuritygroups':
            # Verificar si es una instancia virtual con subnet específica
            if '_virtual_subnet_id' in item:
                # Es una instancia virtual - asociarla solo a su subnet específica
                subnet_id = item['_virtual_subnet_id']
                vnet_id = _get_parent_id(subnet_id, 'vnet')
                rg_id = _get_parent_id(vnet_id, 'rg') if vnet_id else None
                sub_id = _get_parent_id(rg_id, 'sub') if rg_id else None
                
                if sub_id and sub_id in subs and rg_id in subs[sub_id]['resource_groups'] and vnet_id in subs[sub_id]['resource_groups'][rg_id]['vnets'] and subnet_id in subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id]['subnets']:
                    subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id]['subnets'][subnet_id]['resources'].append(i)
            else:
                # NSG original - SIEMPRE va como standalone en su RG, sin importar las subnets
                rg_id = _get_parent_id(item_id, 'rg')
                sub_id = _get_parent_id(rg_id, 'sub') if rg_id else None
                if rg_id and sub_id and sub_id in subs and rg_id in subs[sub_id]['resource_groups']:
                    subs[sub_id]['resource_groups'][rg_id]['standalone_resources'].append(i)
            continue  # Saltar el procesamiento normal para NSGs

        # Manejo especial para Route Tables que pueden estar en múltiples subnets
        if item_type == 'microsoft.network/routetables':
            # Verificar si es una instancia virtual con subnet específica
            if '_virtual_subnet_id' in item:
                # Es una instancia virtual - asociarla solo a su subnet específica
                subnet_id = item['_virtual_subnet_id']
                vnet_id = _get_parent_id(subnet_id, 'vnet')
                rg_id = _get_parent_id(vnet_id, 'rg') if vnet_id else None
                sub_id = _get_parent_id(rg_id, 'sub') if rg_id else None
                
                if sub_id and sub_id in subs and rg_id in subs[sub_id]['resource_groups'] and vnet_id in subs[sub_id]['resource_groups'][rg_id]['vnets'] and subnet_id in subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id]['subnets']:
                    subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id]['subnets'][subnet_id]['resources'].append(i)
            else:
                # Route Table original - SIEMPRE va como standalone en su RG, sin importar las subnets
                rg_id = _get_parent_id(item_id, 'rg')
                sub_id = _get_parent_id(rg_id, 'sub') if rg_id else None
                if rg_id and sub_id and sub_id in subs and rg_id in subs[sub_id]['resource_groups']:
                    subs[sub_id]['resource_groups'][rg_id]['standalone_resources'].append(i)
            continue  # Saltar el procesamiento normal para Route Tables

        # Procesamiento normal para otros tipos de recursos
        subnet_id = _find_subnet_for_resource(item, nic_to_subnet_map)
        
        if subnet_id:
            subnet_id = subnet_id.lower()
            vnet_id = _get_parent_id(subnet_id, 'vnet')
            rg_id = _get_parent_id(vnet_id, 'rg') if vnet_id else None
            sub_id = _get_parent_id(rg_id, 'sub') if rg_id else None
            
            if sub_id and sub_id in subs and rg_id in subs[sub_id]['resource_groups'] and vnet_id in subs[sub_id]['resource_groups'][rg_id]['vnets'] and subnet_id in subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id]['subnets']:
                subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id]['subnets'][subnet_id]['resources'].append(i)
            else: # Si la subnet no existe en la jerarquía, tratar como standalone en el RG
                rg_id = _get_parent_id(item_id, 'rg')
                if rg_id and sub_id in subs and rg_id in subs[sub_id]['resource_groups']:
                    subs[sub_id]['resource_groups'][rg_id]['standalone_resources'].append(i)
        else:
            # Si no está en una subnet, ver si está en una VNet directamente
            vnet_id = _get_parent_id(item_id, 'vnet')
            if vnet_id:
                rg_id = _get_parent_id(vnet_id, 'rg')
                sub_id = _get_parent_id(rg_id, 'sub') if rg_id else None
                if sub_id and sub_id in subs and rg_id in subs[sub_id]['resource_groups'] and vnet_id in subs[sub_id]['resource_groups'][rg_id]['vnets']:
                    subs[sub_id]['resource_groups'][rg_id]['vnets'][vnet_id]['direct_resources'].append(i)
                else: # Fallback a standalone en RG
                    rg_id = _get_parent_id(item_id, 'rg')
                    if rg_id and sub_id in subs and rg_id in subs[sub_id]['resource_groups']:
                        subs[sub_id]['resource_groups'][rg_id]['standalone_resources'].append(i)
            else: # Finalmente, es un recurso standalone en un RG
                rg_id = _get_parent_id(item_id, 'rg')
                sub_id = _get_parent_id(rg_id, 'sub') if rg_id else None
                if sub_id and sub_id in subs and rg_id in subs[sub_id]['resource_groups']:
                    subs[sub_id]['resource_groups'][rg_id]['standalone_resources'].append(i)

    # 2. Calcular layout y generar contenedores (bottom-up)
    subscription_layouts = {}
    for sub_id, sub_data in subs.items():
        rg_layouts = {}
        for rg_id, rg_data in sub_data['resource_groups'].items():
            
            # Layout para recursos standalone en el RG
            standalone_layout = _calculate_grid_layout(rg_data['standalone_resources'], RESOURCES_PER_ROW['rg'])
            
            # Layout para VNets
            vnet_layouts = {}
            for vnet_id, vnet_data in rg_data['vnets'].items():
                
                # Layout para recursos directos en la VNet
                direct_res_layout = _calculate_grid_layout(vnet_data['direct_resources'], RESOURCES_PER_ROW['vnet'])
                
                # Layout para Subnets
                subnet_layouts = {}
                for subnet_id, subnet_data in vnet_data['subnets'].items():
                    subnet_layout = _calculate_grid_layout(subnet_data['resources'], RESOURCES_PER_ROW['subnet'])
                    subnet_layouts[subnet_id] = {
                        'item_index': subnet_data.get('item_index'),
                        'layout': subnet_layout,
                        'size': _get_required_size(subnet_layout, MIN_WIDTH['subnet'], MIN_HEIGHT['subnet'])
                    }
                
                vnet_layouts[vnet_id] = {
                    'item_index': vnet_data.get('item_index'),
                    'direct_resources_layout': direct_res_layout,
                    'subnet_layouts': subnet_layouts
                }

            rg_layouts[rg_id] = {
                'item_index': rg_data.get('item_index'),
                'standalone_layout': standalone_layout,
                'vnet_layouts': vnet_layouts
            }
        subscription_layouts[sub_id] = {'rg_layouts': rg_layouts}

    # 3. Agrupar suscripciones por tenant para evitar mezclas
    tenant_groups = {}
    for sub_id, sub_layout_data in subscription_layouts.items():
        # Buscar el item de subscripción para obtener el tenantId
        sub_item_index, sub_item = item_map.get(sub_id, (None, None))
        if not sub_item:
            # Si no encontramos el item de subscripción, buscamos uno por el ID
            for i, item in enumerate(items):
                if item['id'].lower() == sub_id:
                    sub_item_index = i
                    sub_item = item
                    break
        
        tenant_id = sub_item.get('tenantId', 'unknown') if sub_item else 'unknown'
        
        if tenant_id not in tenant_groups:
            tenant_groups[tenant_id] = []
        tenant_groups[tenant_id].append((sub_id, sub_layout_data, sub_item_index, sub_item))

    # 4. Posicionar todo (agrupado por tenant)
    current_x = PADDING['left']
    tenant_counter = 0
    
    for tenant_id, tenant_subs in tenant_groups.items():
        print(f"🏢 Posicionando tenant {tenant_id} con {len(tenant_subs)} suscripciones")
        
        current_y = PADDING['top']
        max_tenant_width = 0
        sub_counter = 0
        
        for sub_id, sub_layout_data, sub_item_index, sub_item in tenant_subs:

            sub_name = sub_item.get('name') if sub_item else sub_id.split('/')[-1]

            rg_layouts_for_sub = sub_layout_data.get('rg_layouts', {})
            rg_positions_in_sub, sub_size = _calculate_container_grid_layout(
                rg_layouts_for_sub, 
                lambda rg_layout: _calculate_rg_size(rg_layout)
            )

            # Crear container de Subscription posicionado por tenant
            sub_group_id = f"group_sub_{sub_counter}"
            sub_counter += 1
            
            sub_width = sub_size[0] + PADDING['left'] + PADDING['right']
            sub_height = sub_size[1] + PADDING['top'] + PADDING['bottom']
            
            group_info.append({
                'id': sub_group_id, 'parent_id': '1', 'type': 'subscription_container',
                'x': current_x, 'y': current_y,
                'width': sub_width, 'height': sub_height,
                'label': '', 'style': CONTAINER_STYLES['subscription']
            })
            if sub_item_index is not None:
                # Colocar el icono de la subscripción dentro del contenedor, en la esquina superior izquierda
                node_positions[sub_item_index] = (20, 20)
                resource_to_parent_id[sub_item_index] = sub_group_id

            # Actualizar máximo ancho del tenant para calcular el próximo offset x
            max_tenant_width = max(max_tenant_width, sub_width)        # Offset vertical para dejar espacio para el icono de la suscripción
            content_start_y_sub = PADDING['top'] + 60

            rg_counter = 0
            rg_start_index = len(group_info)  # para insertar rectángulos de región antes de los RG
            region_bounds = {}  # location -> [min_x, min_y, max_x, max_y]

            for rg_id, rg_pos in rg_positions_in_sub.items():
                rg_layout = rg_layouts_for_sub[rg_id]
                rg_size = _calculate_rg_size(rg_layout)
                rg_item_index = rg_layout.get('item_index')
                
                rg_group_id = f"{sub_group_id}_rg_{rg_counter}"
                rg_counter += 1
                
                # Posición relativa al contenedor de la subscripción, con offset
                rg_rel_x = rg_pos[0] + PADDING['left']
                rg_rel_y = rg_pos[1] + content_start_y_sub

                group_info.append({
                    'id': rg_group_id, 'parent_id': sub_group_id, 'type': 'rg_container',
                    'x': rg_rel_x, 'y': rg_rel_y,
                    'width': rg_size[0], 'height': rg_size[1],
                    'label': '', 'style': CONTAINER_STYLES['resource_group']
                })
                if rg_item_index is not None:
                    node_positions[rg_item_index] = (20, 20) # Relativo al padre (RG container)
                    resource_to_parent_id[rg_item_index] = rg_group_id

                # Acumular el bounding box de esta región (según el location propio del RG)
                rg_location = extended_items[rg_item_index].get('location') if rg_item_index is not None else None
                if rg_location:
                    b = region_bounds.setdefault(rg_location, [rg_rel_x, rg_rel_y, rg_rel_x + rg_size[0], rg_rel_y + rg_size[1]])
                    b[0] = min(b[0], rg_rel_x)
                    b[1] = min(b[1], rg_rel_y)
                    b[2] = max(b[2], rg_rel_x + rg_size[0])
                    b[3] = max(b[3], rg_rel_y + rg_size[1])

                # Posicionar contenido del RG (pasando la posición absoluta)
                rg_abs_x = PADDING['left'] + rg_rel_x
                rg_abs_y = current_y + rg_rel_y
                _position_rg_content(
                    rg_layout, rg_group_id, (rg_abs_x, rg_abs_y),
                    group_info, node_positions, resource_to_parent_id, extended_items
                )

            # Si la suscripción abarca más de una región, dibujar un rectángulo discontinuo
            # detrás de los Resource Groups de cada región (convención de draw.io para regiones)
            if len(region_bounds) >= 2:
                region_entries = []
                for region_counter, (location, (min_x, min_y, max_x, max_y)) in enumerate(region_bounds.items()):
                    region_entries.append({
                        'id': f"{sub_group_id}_region_{region_counter}", 'parent_id': sub_group_id, 'type': 'region_container',
                        'x': min_x - REGION_MARGIN, 'y': min_y - REGION_MARGIN,
                        'width': (max_x - min_x) + 2 * REGION_MARGIN, 'height': (max_y - min_y) + 2 * REGION_MARGIN,
                        'label': f"📍 {location}", 'style': CONTAINER_STYLES['region']
                    })
                group_info[rg_start_index:rg_start_index] = region_entries

            current_y += sub_size[1] + PADDING['top'] + PADDING['bottom'] + RG_GRID_SPACING['y']

    print("✅ Layout de red jerárquico completado.")
    return extended_items, node_positions, group_info, resource_to_parent_id

def _calculate_grid_layout(resource_indices: List[int], per_row: int) -> Dict[int, Tuple[int, int]]:
    """Calcula posiciones en una grid simple para una lista de recursos."""
    layout = {}
    if not resource_indices:
        return layout
    
    for i, res_index in enumerate(resource_indices):
        row = i // per_row
        col = i % per_row
        x = col * RESOURCE_SPACING['x']
        y = row * RESOURCE_SPACING['y']
        layout[res_index] = (x, y)
    return layout

def _get_required_size(layout: Dict, min_width: int, min_height: int) -> Tuple[int, int]:
    """Calcula el tamaño necesario para albergar un layout de grid."""
    if not layout:
        return (min_width, min_height)
    
    max_x = max(pos[0] for pos in layout.values()) if layout else 0
    max_y = max(pos[1] for pos in layout.values()) if layout else 0
    
    width = max_x + PADDING['left'] + PADDING['right'] + 100 # 100 para el icono
    height = max_y + PADDING['top'] + PADDING['bottom'] + 100
    
    return (max(width, min_width), max(height, min_height))

def _calculate_vnet_size(vnet_layout: Dict) -> Tuple[int, int]:
    """Calcula el tamaño de un contenedor de VNet."""
    # Calcular tamaño para subnets
    subnet_layouts = vnet_layout['subnet_layouts']
    subnet_positions, total_size = _calculate_container_grid_layout(
        subnet_layouts,
        lambda sl: sl['size'],
        cols=1 # Subnets en una sola columna
    )
    
    # Calcular tamaño para recursos directos
    direct_res_size = _get_required_size(vnet_layout['direct_resources_layout'], 0, 0)
    
    # El ancho es el máximo entre subnets y recursos directos
    # La altura es la suma
    width = max(total_size[0], direct_res_size[0]) + PADDING['left'] + PADDING['right']
    height = total_size[1] + direct_res_size[1] + VNET_SPACING['y']
    
    return (max(width, MIN_WIDTH['vnet']), max(height, MIN_HEIGHT['vnet']))

def _calculate_rg_size(rg_layout: Dict) -> Tuple[int, int]:
    """Calcula el tamaño de un contenedor de Resource Group."""
    vnet_layouts = rg_layout['vnet_layouts']
    vnet_positions, vnets_total_size = _calculate_container_grid_layout(
        vnet_layouts,
        lambda vl: _calculate_vnet_size(vl),
        cols=1 # VNets en una sola columna
    )
    
    standalone_size = _get_required_size(rg_layout['standalone_layout'], 0, 0)
    
    width = max(vnets_total_size[0], standalone_size[0]) + PADDING['left'] + PADDING['right']
    height = vnets_total_size[1] + standalone_size[1] + VNET_SPACING['y']
    
    return (max(width, 0), max(height, MIN_HEIGHT['rg']))

def _calculate_container_grid_layout(layouts: Dict, size_func, cols: int = 2) -> Tuple[Dict, Tuple[int, int]]:
    """
    Calcula posiciones y tamaño total para una grid de contenedores de tamaño variable.
    """
    if not layouts:
        return {}, (0, 0)

    positions = {}
    row_heights = [0] * (len(layouts) // cols + 1)
    current_x = [0] * len(row_heights)
    
    max_width = 0
    current_y = 0
    
    items = list(layouts.items())
    
    row_widths = [0] * (len(items) // cols + 1)
    col_widths = [0] * cols

    # Primero, calcular el ancho máximo de cada columna
    for i, (item_id, layout) in enumerate(items):
        size = size_func(layout)
        col = i % cols
        col_widths[col] = max(col_widths[col], size[0])

    total_grid_width = sum(col_widths) + (RG_GRID_SPACING['x'] * (cols -1))

    # Ahora, posicionar
    x_offsets = [0] * cols
    for i in range(1, cols):
        x_offsets[i] = x_offsets[i-1] + col_widths[i-1] + RG_GRID_SPACING['x']

    y_offset = 0
    row_max_height = 0

    for i, (item_id, layout) in enumerate(items):
        size = size_func(layout)
        row = i // cols
        col = i % cols

        if col == 0 and i > 0:
            y_offset += row_max_height + RG_GRID_SPACING['y']
            row_max_height = 0

        positions[item_id] = (x_offsets[col], y_offset)
        row_max_height = max(row_max_height, size[1])

    total_grid_height = y_offset + row_max_height

    return positions, (total_grid_width, total_grid_height)


def _position_rg_content(rg_layout, rg_group_id, rg_pos, group_info, node_positions, resource_to_parent_id, extended_items):
    """Posiciona todo el contenido (VNets, Subnets, Recursos) dentro de un RG."""
    
    vnet_layouts = rg_layout['vnet_layouts']
    vnet_positions, vnets_total_size = _calculate_container_grid_layout(
        vnet_layouts, lambda vl: _calculate_vnet_size(vl), cols=1
    )
    
    # Offset vertical para dejar espacio para el icono del RG en la parte superior.
    content_start_y = PADDING['top'] + 60
    current_y = content_start_y
    
    vnet_counter = 0
    for vnet_id, vnet_pos_in_rg in vnet_positions.items():
        vnet_layout = vnet_layouts[vnet_id]
        vnet_size = _calculate_vnet_size(vnet_layout)
        vnet_item_index = vnet_layout.get('item_index')
        vnet_name = extended_items[vnet_item_index].get('name') if vnet_item_index is not None else "VNet"
        
        vnet_group_id = f"{rg_group_id}_vnet_{vnet_counter}"
        vnet_counter += 1
        
        vnet_abs_x = rg_pos[0] + PADDING['left']
        vnet_abs_y = rg_pos[1] + current_y
        
        group_info.append({
            'id': vnet_group_id, 'parent_id': rg_group_id, 'type': 'vnet_container',
            'x': PADDING['left'], 'y': current_y,
            'width': vnet_size[0], 'height': vnet_size[1],
            'label': '', 'style': CONTAINER_STYLES['vnet']
        })
        if vnet_item_index is not None:
            node_positions[vnet_item_index] = (20, 20)
            resource_to_parent_id[vnet_item_index] = vnet_group_id

        # Posicionar contenido de la VNet
        _position_vnet_content(
            vnet_layout, vnet_group_id, (vnet_abs_x, vnet_abs_y),
            group_info, node_positions, resource_to_parent_id, extended_items
        )
        current_y += vnet_size[1] + VNET_SPACING['y']

    # Posicionar recursos standalone
    standalone_layout = rg_layout['standalone_layout']
    for res_index, res_pos in standalone_layout.items():
        node_positions[res_index] = (res_pos[0] + PADDING['left'], res_pos[1] + current_y)
        resource_to_parent_id[res_index] = rg_group_id


def _position_vnet_content(vnet_layout, vnet_group_id, vnet_pos, group_info, node_positions, resource_to_parent_id, extended_items):
    """Posiciona Subnets y recursos directos dentro de una VNet."""
    
    subnet_layouts = vnet_layout['subnet_layouts']
    subnet_positions, _ = _calculate_container_grid_layout(
        subnet_layouts, lambda sl: sl['size'], cols=1
    )
    
    current_y = PADDING['top']
    subnet_counter = 0
    for subnet_id, subnet_pos_in_vnet in subnet_positions.items():
        subnet_layout_data = subnet_layouts[subnet_id]
        subnet_size = subnet_layout_data['size']
        subnet_item_index = subnet_layout_data.get('item_index')
        subnet_name = extended_items[subnet_item_index].get('name') if subnet_item_index is not None else "Subnet"
        
        subnet_group_id = f"{vnet_group_id}_subnet_{subnet_counter}"
        subnet_counter += 1
        
        subnet_abs_x = vnet_pos[0] + PADDING['left']
        subnet_abs_y = vnet_pos[1] + current_y
        
        group_info.append({
            'id': subnet_group_id, 'parent_id': vnet_group_id, 'type': 'subnet_container',
            'x': PADDING['left'], 'y': current_y,
            'width': subnet_size[0], 'height': subnet_size[1],
            'label': '', 'style': CONTAINER_STYLES['subnet']
        })
        if subnet_item_index is not None:
            node_positions[subnet_item_index] = (20, 20)
            resource_to_parent_id[subnet_item_index] = subnet_group_id

        # Offset vertical para dejar espacio para el icono de la subnet.
        content_start_y_subnet = PADDING['top'] + 60

        # Posicionar recursos de la subnet
        for res_index, res_pos in subnet_layout_data['layout'].items():
            node_positions[res_index] = (res_pos[0] + PADDING['left'], res_pos[1] + content_start_y_subnet)
            resource_to_parent_id[res_index] = subnet_group_id
            
        current_y += subnet_size[1] + SUBNET_SPACING['y']

    # Posicionar recursos directos de la VNet
    direct_res_layout = vnet_layout['direct_resources_layout']
    for res_index, res_pos in direct_res_layout.items():
        node_positions[res_index] = (res_pos[0] + PADDING['left'], res_pos[1] + current_y)
        resource_to_parent_id[res_index] = vnet_group_id

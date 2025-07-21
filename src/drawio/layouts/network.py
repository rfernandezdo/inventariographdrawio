"""
Network layout module for draw.io diagrams.

This module provides the network layout algorithm that organizes Azure resources
in a hierarchical network-oriented structure, focusing on network architecture
and relationships between VNets, subnets, and network resources.
"""

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

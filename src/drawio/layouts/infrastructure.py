"""
Layout para diagrama de infraestructura - árbol jerárquico usando dependencias estructurales
"""

import math
from .utils import normalize_azure_id, extract_resource_name


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

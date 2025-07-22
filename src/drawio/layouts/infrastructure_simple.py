"""
Layout simple y seguro para diagrama de infraestructura.
Evita recursión para prevenir bucles infinitos.
"""

def generate_infrastructure_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """
    Layout simple y seguro para infraestructura sin recursión.
    """
    print("🌳 Generando layout de infraestructura (versión simplificada y segura)...")
    
    node_positions = {}
    group_info = []
    resource_to_parent_id = {}
    tree_edges = []
    
    # Configuración de layout
    level_spacing = 150
    horizontal_spacing = 180
    base_x = 100
    base_y = 100
    
    # Layout simple por niveles sin recursión
    current_y = base_y
    
    # Procesar cada nivel de manera secuencial
    for level_num in [0, 1, 2, 3]:
        if level_num not in levels:
            continue
            
        print(f"📍 Procesando nivel {level_num} con {len(levels[level_num])} elementos")
        
        current_x = base_x
        max_items_per_row = 6  # Máximo elementos por fila
        items_in_current_row = 0
        
        for idx, item in levels[level_num]:
            # Calcular posición
            x = current_x
            y = current_y
            
            # Posicionar el nodo
            node_positions[idx] = (x, y)
            
            # Crear información del grupo si es un contenedor
            item_type = item.get('type', '').lower()
            if item_type in ['microsoft.management/managementgroups', 
                           'microsoft.resources/subscriptions',
                           'microsoft.resources/subscriptions/resourcegroups']:
                
                group_style = get_container_style(item_type)
                group_info.append({
                    'id': f'container_{idx}',
                    'parent_id': '1',  # Todos los contenedores van al root
                    'type': 'container',
                    'x': x - 20,
                    'y': y - 20, 
                    'width': 160,
                    'height': 100,
                    'label': item.get('name', 'Unknown'),
                    'style': group_style
                })
                
                resource_to_parent_id[idx] = f'container_{idx}'
            
            # Mover a la siguiente posición
            current_x += horizontal_spacing
            items_in_current_row += 1
            
            # Nueva fila si alcanzamos el máximo
            if items_in_current_row >= max_items_per_row:
                current_x = base_x
                current_y += 120  # Espaciado vertical entre filas
                items_in_current_row = 0
        
        # Mover al siguiente nivel
        current_y += level_spacing
    
    # Generar edges jerárquicos básicos basados en dependencias
    for src_id, tgt_id in dependencies:
        src_id_lower = src_id.lower()
        tgt_id_lower = tgt_id.lower()
        
        # Buscar índices
        src_idx = None
        tgt_idx = None
        
        for i, item in enumerate(items):
            item_id_lower = item['id'].lower()
            if item_id_lower == src_id_lower:
                src_idx = i
            elif item_id_lower == tgt_id_lower:
                tgt_idx = i
        
        if src_idx is not None and tgt_idx is not None:
            # Verificar que ambos nodos estén posicionados
            if src_idx in node_positions and tgt_idx in node_positions:
                tree_edges.append({
                    'source': src_idx,
                    'target': tgt_idx,
                    'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#666666;strokeWidth=1;'
                })
    
    print(f"✅ Layout completado: {len(node_positions)} nodos, {len(group_info)} grupos, {len(tree_edges)} edges")
    
    return node_positions, group_info, resource_to_parent_id, tree_edges


def get_container_style(item_type):
    """Retorna el estilo apropiado para cada tipo de contenedor"""
    if 'managementgroup' in item_type:
        return 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;'
    elif 'subscription' in item_type and 'resourcegroup' not in item_type:
        return 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;fontStyle=1;'
    elif 'resourcegroup' in item_type:
        return 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=11;fontStyle=1;'
    else:
        return 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=10;'

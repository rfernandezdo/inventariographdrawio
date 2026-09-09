"""
Layout para diagrama de componentes - agrupado por función/tipo
"""

from .utils import classify_network_resource, group_resources_by_type, classify_component_category, COMPONENT_CATEGORIES


def generate_components_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """Disposición para diagrama de componentes - agrupado por función/tipo"""
    print("🧩 Generando layout de componentes agrupado por función...")
    
    y_step = 200
    x_step = 220
    node_positions = {}
    
    # Agrupar recursos por tipo/función (misma clasificación que usa el modo 'hld')
    groups = {category: [] for category in COMPONENT_CATEGORIES}
    
    for i, item in enumerate(items):
        resource_type = (item.get('type') or '').lower()
        category = classify_component_category(resource_type)
        # Governance (Management Groups, Suscripciones, Resource Groups) queda fuera:
        # un diagrama de componentes es un bill of materials de tecnologías concretas,
        # no de ámbitos organizativos de Azure. Ya se muestran en el modo 'infrastructure'.
        if category is None:
            continue
        groups[category].append((i, item))
    
    print("📊 Distribución por grupos:")
    for group_name, group_items in groups.items():
        if group_items:
            print(f"   {group_name}: {len(group_items)} recursos")
    
    # Posicionar grupos verticalmente
    group_y = 100  # Espacio para títulos
    total_positioned = 0
    
    for group_name, group_items in groups.items():
        if not group_items:
            continue
        
        print(f"📍 Posicionando grupo {group_name} con {len(group_items)} recursos")
        
        # Agrupar espacialmente por Resource Group para reducir cruces de líneas
        # entre recursos relacionados (mismo RG suele implicar más dependencias entre sí)
        group_items = sorted(group_items, key=lambda pair: pair[1].get('resourceGroup') or '')
        
        # Posicionar recursos del grupo horizontalmente
        x = 100
        resources_per_row = 4  # Máximo 4 recursos por fila (nombres de Azure pueden ser largos)
        current_row = 0
        
        for i, (idx, item) in enumerate(group_items):
            # Calcular posición en grid
            col = i % resources_per_row
            row = i // resources_per_row
            
            pos_x = x + col * x_step
            pos_y = group_y + row * 160  # Espaciado vertical amplio para etiquetas largas
            
            node_positions[idx] = (pos_x, pos_y)
            total_positioned += 1
        
        # Calcular espacio necesario para este grupo
        rows_needed = (len(group_items) + resources_per_row - 1) // resources_per_row
        group_height = max(160, rows_needed * 160)  # Altura mínima de 160px
        
        group_y += group_height + y_step  # Espacio entre grupos
    
    print(f"✅ Layout de componentes completado: {total_positioned} recursos posicionados")
    return node_positions


def classify_resource_by_function(resource_type):
    """
    Clasifica un recurso por su función principal.

    Alias sobre classify_component_category (Governance -> 'Other' en vez de
    excluir, ya que el uso original de este helper esperaba una categoría
    siempre no-nula).

    Args:
        resource_type (str): Tipo de recurso de Azure
        
    Returns:
        str: Categoría funcional
    """
    return classify_component_category(resource_type) or 'Other'

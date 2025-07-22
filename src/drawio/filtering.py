"""
Filtrado de recursos y dependencias.

Este módulo maneja el filtrado de recursos de Azure y sus dependencias
según criterios de inclusión y exclusión especificados por el usuario.
"""


def filter_items_and_dependencies(items, dependencies, include_ids=None, exclude_ids=None):
    """
    Filtra recursos y dependencias según criterios de inclusión/exclusión.
    
    Args:
        items: Lista de recursos de Azure
        dependencies: Lista de dependencias entre recursos
        include_ids: IDs específicos a incluir (incluye descendientes)
        exclude_ids: IDs específicos a excluir (excluye descendientes)
    
    Returns:
        tuple: (items_filtrados, dependencies_filtradas)
    """
    if not include_ids and not exclude_ids:
        return items, dependencies
    
    # Normalizar IDs a lowercase para comparación
    include_ids = set(i.lower() for i in include_ids) if include_ids else None
    exclude_ids = set(i.lower() for i in exclude_ids) if exclude_ids else set()
    
    # Crear mapa de dependencias hijos -> padre para encontrar descendientes
    child_map = {}
    for src, tgt in dependencies:
        child_map.setdefault(tgt, set()).add(src)
    
    def collect_descendants(start_ids):
        """
        Recolecta recursivamente todos los descendientes de los IDs dados.
        
        Args:
            start_ids: Conjunto de IDs de partida
        
        Returns:
            set: Todos los IDs descendientes encontrados
        """
        result = set()
        stack = list(start_ids)
        
        while stack:
            current = stack.pop()
            if current not in result:
                result.add(current)
                # Agregar hijos del elemento actual
                stack.extend(child_map.get(current, []))
        
        return result
    
    # Determinar conjunto de IDs a incluir
    all_ids = set(item['id'].lower() for item in items)
    selected_ids = set()
    
    if include_ids:
        # Incluir IDs especificados y todos sus descendientes
        selected_ids = collect_descendants(include_ids)
        selected_ids.update(include_ids)
    else:
        # Si no se especifican IDs a incluir, incluir todos por defecto
        selected_ids = all_ids
    
    if exclude_ids:
        # Excluir IDs especificados y todos sus descendientes
        to_exclude = collect_descendants(exclude_ids)
        to_exclude.update(exclude_ids)
        selected_ids = selected_ids - to_exclude
    
    # Filtrar items según IDs seleccionados
    filtered_items = [item for item in items if item['id'].lower() in selected_ids]
    
    # Filtrar dependencias - solo mantener las que conectan recursos incluidos
    filtered_dependencies = [
        (src, tgt) for src, tgt in dependencies 
        if src in selected_ids and tgt in selected_ids
    ]
    
    return filtered_items, filtered_dependencies


def filter_by_resource_type(items, dependencies, resource_types=None, exclude_types=None):
    """
    Filtra recursos por tipo de recurso Azure.
    
    Args:
        items: Lista de recursos de Azure
        dependencies: Lista de dependencias entre recursos
        resource_types: Tipos de recursos a incluir (ej: ['microsoft.compute/virtualmachines'])
        exclude_types: Tipos de recursos a excluir
    
    Returns:
        tuple: (items_filtrados, dependencies_filtradas)
    """
    if not resource_types and not exclude_types:
        return items, dependencies
    
    # Normalizar tipos a lowercase
    if resource_types:
        resource_types = set(rt.lower() for rt in resource_types)
    if exclude_types:
        exclude_types = set(et.lower() for et in exclude_types)
    
    # Filtrar items por tipo
    filtered_items = []
    for item in items:
        item_type = (item.get('type') or '').lower()
        
        include_item = True
        
        if resource_types:
            include_item = include_item and item_type in resource_types
        
        if exclude_types:
            include_item = include_item and item_type not in exclude_types
        
        if include_item:
            filtered_items.append(item)
    
    # Crear conjunto de IDs incluidos
    included_ids = set(item['id'].lower() for item in filtered_items)
    
    # Filtrar dependencias
    filtered_dependencies = [
        (src, tgt) for src, tgt in dependencies 
        if src.lower() in included_ids and tgt.lower() in included_ids
    ]
    
    return filtered_items, filtered_dependencies


def filter_by_subscription(items, dependencies, subscription_ids=None, exclude_subscription_ids=None):
    """
    Filtra recursos por suscripción Azure.
    
    Args:
        items: Lista de recursos de Azure
        dependencies: Lista de dependencias entre recursos
        subscription_ids: IDs de suscripciones a incluir
        exclude_subscription_ids: IDs de suscripciones a excluir
    
    Returns:
        tuple: (items_filtrados, dependencies_filtradas)
    """
    if not subscription_ids and not exclude_subscription_ids:
        return items, dependencies
    
    # Normalizar IDs de suscripción
    if subscription_ids:
        subscription_ids = set(sid.lower() for sid in subscription_ids)
    if exclude_subscription_ids:
        exclude_subscription_ids = set(sid.lower() for sid in exclude_subscription_ids)
    
    def extract_subscription_id(azure_id):
        """Extrae el ID de suscripción de un ID de recurso Azure."""
        parts = azure_id.lower().split('/')
        try:
            if 'subscriptions' in parts:
                sub_index = parts.index('subscriptions')
                if sub_index + 1 < len(parts):
                    return parts[sub_index + 1]
        except (ValueError, IndexError):
            pass
        return None
    
    # Filtrar items por suscripción
    filtered_items = []
    for item in items:
        item_sub_id = extract_subscription_id(item['id'])
        
        include_item = True
        
        if subscription_ids and item_sub_id:
            include_item = include_item and item_sub_id in subscription_ids
        
        if exclude_subscription_ids and item_sub_id:
            include_item = include_item and item_sub_id not in exclude_subscription_ids
        
        if include_item:
            filtered_items.append(item)
    
    # Crear conjunto de IDs incluidos
    included_ids = set(item['id'].lower() for item in filtered_items)
    
    # Filtrar dependencias
    filtered_dependencies = [
        (src, tgt) for src, tgt in dependencies 
        if src.lower() in included_ids and tgt.lower() in included_ids
    ]
    
    return filtered_items, filtered_dependencies


def filter_by_location(items, dependencies, locations=None, exclude_locations=None):
    """
    Filtra recursos por ubicación/región Azure.
    
    Args:
        items: Lista de recursos de Azure
        dependencies: Lista de dependencias entre recursos
        locations: Ubicaciones a incluir (ej: ['eastus', 'westeurope'])
        exclude_locations: Ubicaciones a excluir
    
    Returns:
        tuple: (items_filtrados, dependencies_filtradas)
    """
    if not locations and not exclude_locations:
        return items, dependencies
    
    # Normalizar ubicaciones
    if locations:
        locations = set(loc.lower() for loc in locations)
    if exclude_locations:
        exclude_locations = set(loc.lower() for loc in exclude_locations)
    
    # Filtrar items por ubicación
    filtered_items = []
    for item in items:
        item_location = (item.get('location') or '').lower()
        
        include_item = True
        
        if locations:
            include_item = include_item and item_location in locations
        
        if exclude_locations:
            include_item = include_item and item_location not in exclude_locations
        
        if include_item:
            filtered_items.append(item)
    
    # Crear conjunto de IDs incluidos
    included_ids = set(item['id'].lower() for item in filtered_items)
    
    # Filtrar dependencias
    filtered_dependencies = [
        (src, tgt) for src, tgt in dependencies 
        if src.lower() in included_ids and tgt.lower() in included_ids
    ]
    
    return filtered_items, filtered_dependencies

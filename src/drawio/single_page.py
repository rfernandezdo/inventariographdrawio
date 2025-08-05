"""
Generación de archivos draw.io de página única.

Este módulo maneja la creación de archivos draw.io con una sola página,
según el modo de diagrama especificado (infrastructure, components, network).
"""

import xml.etree.ElementTree as ET
import json


def generate_drawio_file(items, dependencies, embed_data=True, include_ids=None, diagram_mode='infrastructure', no_hierarchy_edges=False):
    """
    Función principal para generar archivos draw.io de página única.
    
    Args:
        items: Lista de recursos de Azure
        dependencies: Lista de dependencias entre recursos
        embed_data: Si incrustar datos completos o solo el tipo
        include_ids: IDs específicos a incluir
        diagram_mode: Modo del diagrama ('infrastructure', 'components', 'network', 'all')
        no_hierarchy_edges: Si aplicar filtrado de enlaces jerárquicos
    
    Returns:
        str: Contenido XML del archivo draw.io
    """
    # Si el modo es 'all', delegar a la función multipágina
    if diagram_mode == 'all':
        try:
            from .multipage import generate_drawio_multipage_file
            return generate_drawio_multipage_file(items, dependencies, embed_data, include_ids, no_hierarchy_edges)
        except ImportError:
            # Fallback a función legacy si el módulo no está disponible
            from ..drawio_export import generate_drawio_multipage_file as legacy_multipage
            return legacy_multipage(items, dependencies, embed_data, include_ids, no_hierarchy_edges)
    
    # Importar funciones necesarias desde otros módulos
    try:
        from ..xml_builder import pretty_print_xml
        from ..layouts.infrastructure import generate_infrastructure_layout
        from ..layouts.components import generate_components_layout 
        from ..layouts.network import generate_network_layout
        from ..styles import get_node_style
    except ImportError:
        # Fallback a funciones legacy desde drawio_export.py
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from drawio_export import (
            pretty_print_xml,
            generate_infrastructure_layout,
            generate_components_layout, 
            generate_network_layout,
            get_node_style
        )
    
    print("INFO: Generando el archivo .drawio...")
    
    # Crear estructura básica del archivo draw.io
    mxfile = ET.Element("mxfile", host="app.diagrams.net", agent="python-script")
    diagram = ET.SubElement(mxfile, "diagram", id="main-diagram", name="Azure Infrastructure")
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel", 
                                dx="2500", dy="2000", grid="1", gridSize="10", 
                                guides="1", tooltips="1", connect="1", arrows="1", 
                                fold="1", page="1", pageScale="1", 
                                pageWidth="4681", pageHeight="3300")
    root = ET.SubElement(mxGraphModel, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    # Organizar recursos por niveles jerárquicos
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

    # Generar layout según el modo
    node_positions, group_info, resource_to_parent_id = {}, [], {}
    tree_edges = []  # Para almacenar las conexiones del árbol
    
    if diagram_mode == 'network':
        extended_items, node_positions, group_info, resource_to_parent_id = generate_network_layout(
            items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
        # Usar extended_items para generar el XML, pero mantener items original para compatibilidad
        render_items = extended_items
    elif diagram_mode == 'components':
        render_items = items
        node_positions = generate_components_layout(
            items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
    else:  # 'infrastructure'
        render_items = items
        node_positions, group_info, resource_to_parent_id, tree_edges = generate_infrastructure_layout(
            items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)

    # Fallback de posicionamiento para nodos sin posición
    for i, item in enumerate(render_items):
        if i not in node_positions:
            node_positions[i] = ((i % 15) * 180, 1500 + (i // 15) * 150)

    # Crear agrupadores (contenedores)
    _create_containers(root, group_info)

    # Crear nodos de recursos
    _create_resource_nodes(root, render_items, node_positions, resource_to_parent_id, 
                          azure_id_to_cell_id, get_node_style, diagram_mode, embed_data)

    # Crear dependencias (flechas)
    _create_edges(root, diagram_mode, tree_edges, dependencies, render_items, 
                 azure_id_to_cell_id, no_hierarchy_edges)
            
    return pretty_print_xml(mxfile)


def _create_containers(root, group_info):
    """Crea los contenedores (agrupadores) en el diagrama."""
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


def _create_resource_nodes(root, items, node_positions, resource_to_parent_id, 
                          azure_id_to_cell_id, get_node_style_func, diagram_mode, embed_data):
    """Crea los nodos de recursos en el diagrama."""
    for i, item in enumerate(items):
        cell_id = f"node-{i}"
        azure_id_to_cell_id[item['id'].lower()] = cell_id
        style = get_node_style_func(item.get('type'))
        
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


def _create_edges(root, diagram_mode, tree_edges, dependencies, items, azure_id_to_cell_id, no_hierarchy_edges):
    """Crea las aristas (dependencias) en el diagrama."""
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
            edges_to_create = _filter_network_hierarchical_edges(dependencies, items)
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
    
    # Crear los elementos XML de las aristas
    _create_edge_elements(root, edges_to_create, azure_id_to_cell_id, diagram_mode, tree_edges, items)


def _filter_network_hierarchical_edges(dependencies, items):
    """Filtra enlaces jerárquicos para el modo network con no_hierarchy_edges."""
    print(f"🔗 Filtrando enlaces jerárquicos (Resource Groups y VNet-Subnet) de {len(dependencies)} dependencias")
    
    # Crear diccionario de mapeo ID → tipo una sola vez para eficiencia
    id_to_type = {item['id'].lower(): item.get('type', '').lower() for item in items}
    edges_to_create = []
    
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
    return edges_to_create


def _create_edge_elements(root, edges_to_create, azure_id_to_cell_id, diagram_mode, tree_edges, items):
    """Crea los elementos XML de las aristas."""
    edge_counter = 0
    for source_id, target_id in edges_to_create:
        source_id_lower = source_id.lower()
        target_id_lower = target_id.lower()
        
        if source_id_lower in azure_id_to_cell_id and target_id_lower in azure_id_to_cell_id:
            source_cell = azure_id_to_cell_id[source_id_lower]
            target_cell = azure_id_to_cell_id[target_id_lower]
            
            # Determinar estilo de la flecha
            style = _get_edge_style(diagram_mode, tree_edges, source_id_lower, target_id_lower, items)
            
            edge_cell = ET.SubElement(root, "mxCell", 
                                    id=f"edge-{edge_counter}", 
                                    style=style, 
                                    parent="1", 
                                    source=source_cell, 
                                    target=target_cell, 
                                    edge="1")
            ET.SubElement(edge_cell, "mxGeometry", attrib={'relative': '1', 'as': 'geometry'})
            edge_counter += 1


def _get_edge_style(diagram_mode, tree_edges, source_id_lower, target_id_lower, items):
    """Determina el estilo de una arista según el tipo de conexión."""
    is_hierarchical = False
    is_rg_to_resource = False
    is_vnet_peering = False
    
    # Buscar los items correspondientes
    source_item = None
    target_item = None
    for item in items:
        if item['id'].lower() == source_id_lower:
            source_item = item
        elif item['id'].lower() == target_id_lower:
            target_item = item
    
    # Detectar peering entre VNets
    if source_item and target_item:
        source_type = source_item.get('type', '').lower()
        target_type = target_item.get('type', '').lower()
        
        # Es peering si ambos son VNets
        if (source_type == 'microsoft.network/virtualnetworks' and 
            target_type == 'microsoft.network/virtualnetworks'):
            is_vnet_peering = True
    
    if diagram_mode == 'infrastructure' and tree_edges:
        is_hierarchical = (source_id_lower, target_id_lower) in [(c, p) for c, p in tree_edges]
        
        # Identificar si es una conexión RG → Resource específicamente
        if is_hierarchical and source_item and target_item:
            target_type = target_item.get('type', '').lower()
            source_type = source_item.get('type', '').lower()
            
            # RG es el padre (target) y el recurso es el hijo (source)
            is_rg_to_resource = (target_type == 'microsoft.resources/subscriptions/resourcegroups' and 
                               source_type not in ['microsoft.management/managementgroups', 
                                                 'microsoft.resources/subscriptions',
                                                 'microsoft.resources/subscriptions/resourcegroups'])
    
    # Estilos específicos con VNet peering en primer lugar
    if is_vnet_peering:
        # VNet Peering - línea naranja sólida gruesa
        return "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#FF6B35;strokeWidth=3;dashed=0;"
    elif is_hierarchical and is_rg_to_resource:
        # Conexión RG → Resource - línea sólida RECTA
        return "edgeStyle=straight;rounded=0;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
    elif is_hierarchical:
        # Otras conexiones jerárquicas (MG → Sub, Sub → RG, MG → MG) - línea sólida ORTOGONAL
        return "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
    else:
        # Dependencia no jerárquica - línea punteada ortogonal
        return "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#757575;strokeWidth=1;dashed=1;"

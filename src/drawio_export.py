"""
Funciones para generar el XML de draw.io y gestionar la disposición visual.

NOTA: Este archivo está siendo refactorizado gradualmente hacia una estructura modular.
Los nuevos módulos están en src/drawio/ y gradualmente reemplazarán este archivo.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import json

# Importar desde los nuevos módulos cuando estén disponibles
try:
    # Intentar primero importaciones absolutas
    from drawio.styles import get_node_style as _modular_get_node_style
    from drawio.xml_builder import pretty_print_xml as _modular_pretty_print_xml
    from drawio.layouts.infrastructure import generate_infrastructure_layout as _modular_infrastructure_layout
    from drawio.layouts.components import generate_components_layout as _modular_components_layout
    from drawio.layouts.network import generate_network_layout as _modular_network_layout
    from drawio.layouts.flow import generate_flow_layout as _modular_flow_layout
    from drawio.icons import AZURE_ICONS as _modular_azure_icons, HIDDEN_RESOURCE_TYPES as _modular_hidden_types
    from drawio.styles import HIDDEN_RESOURCE_STYLE as _modular_hidden_style
    from drawio.multipage import generate_drawio_multipage_file as _modular_multipage_file
    from drawio.single_page import generate_drawio_file as _modular_single_page_file
    from drawio.filtering import filter_items_and_dependencies as _modular_filter_items
    _MODULAR_AVAILABLE = True
    print("🔄 Usando módulos refactorizados de src/drawio/")
except ImportError:
    try:
        # Fallback a importaciones relativas
        # Usando versión simple y segura de infrastructure layout
        from .drawio.layouts.infrastructure_simple import generate_infrastructure_layout as _modular_infrastructure_layout
        from .drawio.styles import get_node_style as _modular_get_node_style
        from .drawio.xml_builder import pretty_print_xml as _modular_pretty_print_xml
        from .drawio.layouts.components import generate_components_layout as _modular_components_layout
        from .drawio.layouts.network import generate_network_layout as _modular_network_layout
        from .drawio.layouts.flow import generate_flow_layout as _modular_flow_layout
        from .drawio.icons import AZURE_ICONS as _modular_azure_icons, HIDDEN_RESOURCE_TYPES as _modular_hidden_types
        from .drawio.styles import HIDDEN_RESOURCE_STYLE as _modular_hidden_style
        from .drawio.multipage import generate_drawio_multipage_file as _modular_multipage_file
        from .drawio.single_page import generate_drawio_file as _modular_single_page_file
        from .drawio.filtering import filter_items_and_dependencies as _modular_filter_items
        _MODULAR_AVAILABLE = True
        print("🔄 Usando módulos refactorizados de src/drawio/ con infrastructure simplificada")
        print("🔄 Usando módulos refactorizados de src/drawio/ (importación relativa)")
    except ImportError:
        _MODULAR_AVAILABLE = False
        print("⚠️  Módulos refactorizados no disponibles, usando código legacy")


# --- CONSTANTES LEGACY (FALLBACK) ---
# Solo se usan si los módulos refactorizados no están disponibles

HIDDEN_RESOURCE_TYPES = {
    "microsoft.network/privatednszones/virtualnetworklinks",
}

# Estilo especial para recursos hidden
HIDDEN_RESOURCE_STYLE = "verticalLabelPosition=bottom;verticalAlign=top;html=1;shape=mxgraph.infographic.shadedCube;isoAngle=15;fillColor=#10739E;strokeColor=none;aspect=fixed;"

# Iconos básicos de Azure (versión reducida para fallback)
AZURE_ICONS = {
    "microsoft.management/managementgroups": "img/lib/azure2/general/Management_Groups.svg",
    "microsoft.resources/subscriptions": "img/lib/azure2/general/Subscriptions.svg",
    "microsoft.resources/subscriptions/resourcegroups": "img/lib/azure2/general/Resource_Groups.svg",
    "microsoft.compute/virtualmachines": "img/lib/azure2/compute/Virtual_Machine.svg",
    "microsoft.network/virtualnetworks": "img/lib/azure2/networking/Virtual_Networks.svg",
    "microsoft.network/virtualnetworks/subnets": "img/lib/azure2/networking/Subnet.svg",
    "microsoft.storage/storageaccounts": "img/lib/azure2/storage/Storage_Accounts.svg",
}

FALLBACK_STYLES = {
    "managementgroup": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;shadow=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=14;",
    "subscription": "rounded=1;whiteSpace=wrap;html=1;shadow=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=12;",
    "resourcegroup": "image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image=img/lib/azure2/general/Resource_Groups.svg;",
    "resource": "rounded=1;whiteSpace=wrap;html=1;shadow=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
}

def get_node_style(resource_type):
    if not resource_type:
        return FALLBACK_STYLES['resource']
    
    resource_type_lower = resource_type.lower()
    
    # Verificar si es un recurso hidden
    if resource_type_lower in HIDDEN_RESOURCE_TYPES:
        print(f"🔒 Aplicando estilo hidden a recurso: {resource_type}")
        return HIDDEN_RESOURCE_STYLE
    
    # Obtener icono específico de Azure
    icon_path = AZURE_ICONS.get(resource_type_lower)
    if icon_path:
        return f"image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image={icon_path}"
    
    # Estilos especiales para tipos de contenedores
    if resource_type_lower == 'microsoft.management/managementgroups': 
        return FALLBACK_STYLES['managementgroup']
    if resource_type_lower == 'microsoft.resources/subscriptions': 
        return FALLBACK_STYLES['subscription']
    if resource_type_lower == 'microsoft.resources/subscriptions/resourcegroups': 
        return FALLBACK_STYLES['resourcegroup']
    
    # Estilo genérico para recursos sin icono específico
    return FALLBACK_STYLES['resource']
    return FALLBACK_STYLES['resource']

def pretty_print_xml(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


# === FUNCIONES WRAPPER PARA COMPATIBILIDAD CON MÓDULOS REFACTORIZADOS ===

def get_node_style_wrapper(resource_type):
    """Wrapper que usa módulos refactorizados cuando están disponibles"""
    if _MODULAR_AVAILABLE:
        return _modular_get_node_style(resource_type)
    else:
        return get_node_style(resource_type)

def pretty_print_xml_wrapper(elem):
    """Wrapper que usa módulos refactorizados cuando están disponibles"""
    if _MODULAR_AVAILABLE:
        return _modular_pretty_print_xml(elem)
    else:
        return pretty_print_xml(elem)

def generate_infrastructure_layout_wrapper(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """Wrapper que usa módulos refactorizados cuando están disponibles"""
    if _MODULAR_AVAILABLE:
        return _modular_infrastructure_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
    else:
        return generate_infrastructure_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)

def generate_components_layout_wrapper(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """Wrapper que usa módulos refactorizados cuando están disponibles"""
    if _MODULAR_AVAILABLE:
        return _modular_components_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
    else:
        return generate_components_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)

def generate_network_layout_wrapper(items, dependencies, levels=None, mg_id_to_idx=None, sub_id_to_idx=None, rg_id_to_idx=None):
    """Wrapper que usa módulos refactorizados cuando están disponibles"""
    if _MODULAR_AVAILABLE:
        extended_items, node_positions, group_info, resource_to_parent_id = _modular_network_layout(items, dependencies)
        # Devolver todos los valores incluyendo extended_items para soporte multi-subnet
        return extended_items, node_positions, group_info, resource_to_parent_id
    else:
        # Para la versión legacy, devolver items originales como primer valor
        node_positions, group_info, resource_to_parent_id = generate_network_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
        return items, node_positions, group_info, resource_to_parent_id

def generate_flow_layout_wrapper(items, dependencies):
    """Wrapper que usa el módulo de layout de flujo (izquierda -> derecha)"""
    if _MODULAR_AVAILABLE:
        return _modular_flow_layout(items, dependencies)
    else:
        # Sin módulo disponible: fallback mínimo, grid simple sin capas
        node_positions = {i: ((i % 6) * 180, (i // 6) * 130) for i in range(len(items))}
        return node_positions, [], {}

def generate_drawio_multipage_file_wrapper(items, dependencies, embed_data=True, include_ids=None, no_hierarchy_edges=False):
    """Wrapper que usa módulos refactorizados cuando están disponibles"""
    if _MODULAR_AVAILABLE:
        return _modular_multipage_file(items, dependencies, embed_data, include_ids, no_hierarchy_edges)
    else:
        return generate_drawio_multipage_file(items, dependencies, embed_data, include_ids, no_hierarchy_edges)

def generate_drawio_file_wrapper(items, dependencies, embed_data=True, include_ids=None, diagram_mode='infrastructure', no_hierarchy_edges=False):
    """Wrapper que usa módulos refactorizados cuando están disponibles"""
    if _MODULAR_AVAILABLE:
        return _modular_single_page_file(items, dependencies, embed_data, include_ids, diagram_mode, no_hierarchy_edges)
    else:
        return generate_drawio_file(items, dependencies, embed_data, include_ids, diagram_mode, no_hierarchy_edges)

def filter_items_and_dependencies_wrapper(items, dependencies, include_ids=None, exclude_ids=None):
    """Wrapper que usa módulos refactorizados cuando están disponibles"""
    if _MODULAR_AVAILABLE:
        return _modular_filter_items(items, dependencies, include_ids, exclude_ids)
    else:
        return filter_items_and_dependencies(items, dependencies, include_ids, exclude_ids)


# === FUNCIONES LEGACY (fallback) ===
# Estas funciones son fallbacks mínimos en caso de que los módulos refactorizados fallen

def generate_infrastructure_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """Fallback mínimo para layout de infraestructura"""
    print("⚠️  Usando fallback legacy para infrastructure layout")
    node_positions = {}
    current_y = 100
    for level_num in [0, 1, 2, 3]:
        if level_num in levels:
            current_x = 100
            for idx, item in levels[level_num]:
                node_positions[idx] = (current_x, current_y)
                current_x += 150
            current_y += 150
    return node_positions, [], {}, []

def generate_components_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """Fallback mínimo para layout de componentes"""
    print("⚠️  Usando fallback legacy para components layout")
    y_step = 180
    x_step = 200
    node_positions = {}
    
    # Layout simple por niveles
    current_y = 100
    for level_num in [0, 1, 2, 3]:
        if level_num in levels:
            current_x = 100
            for idx, item in levels[level_num]:
                node_positions[idx] = (current_x, current_y)
                current_x += x_step
            current_y += y_step
    
    return node_positions

def generate_network_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """Fallback mínimo para layout de red"""
    print("⚠️  Usando fallback legacy para network layout")
    
    node_positions = {}
    current_y = 100
    for level_num in [0, 1, 2, 3]:
        if level_num in levels:
            current_x = 100
            for idx, item in levels[level_num]:
                node_positions[idx] = (current_x, current_y)
                current_x += 150
            current_y += 150
    
    return node_positions, [], {}

def generate_drawio_multipage_file(items, dependencies, embed_data=True, include_ids=None, no_hierarchy_edges=False):
    """
    Genera un archivo draw.io con múltiples páginas, cada una con un tipo de diagrama diferente.
    
    Args:
        items: Lista de recursos de Azure
        dependencies: Lista de dependencias entre recursos
        embed_data: Si incrustar datos completos o solo el tipo
        include_ids: IDs específicos a incluir
        no_hierarchy_edges: Si aplicar filtrado de enlaces jerárquicos (solo para página Network)
    
    Returns:
        str: Contenido XML del archivo draw.io con múltiples páginas
    """
    import sys
    import json
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    
    print("INFO: Generando archivo draw.io con múltiples páginas...")
    
    # Crear el elemento raíz del archivo draw.io
    mxfile = ET.Element("mxfile", host="app.diagrams.net", agent="python-script")
    
    # Definir las páginas a generar
    pages = [
        {
            'id': 'infrastructure-page',
            'name': 'Infrastructure',
            'mode': 'infrastructure',
            'description': 'Jerarquía completa de Azure'
        },
        {
            'id': 'components-page', 
            'name': 'Components',
            'mode': 'components',
            'description': 'Agrupado por función y tipo'
        },
        {
            'id': 'network-page',
            'name': 'Network',
            'mode': 'network', 
            'description': 'Recursos de red con enlaces jerárquicos'
        },
        {
            'id': 'network-clean-page',
            'name': 'Network (Clean)',
            'mode': 'network',
            'description': 'Recursos de red sin enlaces jerárquicos',
            'no_hierarchy_edges': True
        }
    ]
    
    # Generar cada página
    for page_info in pages:
        print(f"📄 Generando página: {page_info['name']}")
        
        # Crear el elemento diagram para esta página
        diagram = ET.SubElement(mxfile, "diagram", 
                               id=page_info['id'], 
                               name=page_info['name'])
        
        # Crear el modelo de gráfico
        mxGraphModel = ET.SubElement(diagram, "mxGraphModel", 
                                   dx="2500", dy="2000", grid="1", gridSize="10", 
                                   guides="1", tooltips="1", connect="1", arrows="1", 
                                   fold="1", page="1", pageScale="1", 
                                   pageWidth="4681", pageHeight="3300")
        
        root = ET.SubElement(mxGraphModel, "root")
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")
        
        # Generar el layout específico para esta página
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
        
        node_positions, group_info, resource_to_parent_id = {}, [], {}
        tree_edges = []
        
        # Aplicar filtrado de enlaces jerárquicos si está configurado para esta página
        use_no_hierarchy_edges = page_info.get('no_hierarchy_edges', False)
        
        # Generar layout según el modo
        if page_info['mode'] == 'network':
            extended_items, node_positions, group_info, resource_to_parent_id = generate_network_layout_wrapper(
                items, dependencies)
        elif page_info['mode'] == 'components':
            extended_items = items  # Components no necesita elementos extendidos
            node_positions = generate_components_layout_wrapper(
                items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
        else:  # 'infrastructure'
            extended_items = items  # Infrastructure no necesita elementos extendidos
            node_positions, group_info, resource_to_parent_id, tree_edges = generate_infrastructure_layout_wrapper(
                items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
        
        # Fallback de posicionamiento para nodos sin posición
        for i, item in enumerate(extended_items):
            if i not in node_positions:
                node_positions[i] = ((i % 15) * 180, 1500 + (i // 15) * 150)
        
        # Crear agrupadores (contenedores)
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
        
        # Preparar lista de elementos a renderizar (filtrando Management Groups en modo network,
        # y elementos de gobierno -MG/Subscription/RG- en modo components)
        items_to_render = []
        original_to_filtered_index = {}
        
        for i, item in enumerate(extended_items):
            resource_type_lower = (item.get('type') or '').lower()
            
            # Filtrar Management Groups en modo network
            if page_info['mode'] == 'network' and resource_type_lower == 'microsoft.management/managementgroups':
                continue  # Saltear Management Groups en modo network
            
            # Filtrar elementos de gobierno en modo components (no son "tecnología a implementar")
            if page_info['mode'] == 'components':
                from drawio.filtering import GOVERNANCE_TYPES
                if resource_type_lower in GOVERNANCE_TYPES:
                    continue
            
            # Mapear índice original al filtrado
            filtered_index = len(items_to_render)
            original_to_filtered_index[i] = filtered_index
            items_to_render.append((i, item))
        
        # Crear nodos de recursos
        for filtered_i, (original_i, item) in enumerate(items_to_render):
            cell_id = f"node-{filtered_i}"
            azure_id_to_cell_id[item['id'].lower()] = cell_id
            style = get_node_style_wrapper(item.get('type'))
            
            # En modo network, ajustar estilo para RG, VNet y Subnet
            is_network_container = False
            if page_info['mode'] == 'network':
                resource_type_lower = (item.get('type') or '').lower()
                if resource_type_lower in ['microsoft.resources/subscriptions/resourcegroups', 
                                         'microsoft.network/virtualnetworks', 
                                         'microsoft.network/virtualnetworks/subnets']:
                    is_network_container = True
                    if 'image=' in style:
                        style = style.replace('align=center', 'align=left;labelPosition=right;verticalLabelPosition=middle;verticalAlign=middle')
                elif 'whiteSpace=wrap' not in style:
                    # Recursos individuales (NICs, Private Endpoints, etc.) pueden tener
                    # nombres muy largos; sin wrap invaden a sus vecinos en el grid.
                    if not style.endswith(';'):
                        style += ';'
                    style += 'whiteSpace=wrap;'
            
            # En modo components, permitir que la etiqueta haga wrap dentro de su columna
            # en vez de invadir los nodos vecinos (nombres de Azure pueden ser muy largos,
            # ej. NICs/Private Endpoints con sufijo GUID).
            if page_info['mode'] in ('components', 'flow') and 'whiteSpace=wrap' not in style:
                if not style.endswith(';'):
                    style += ';'
                style += 'whiteSpace=wrap;'
            
            parent_id = resource_to_parent_id.get(original_i, '1')
            
            node_cell = ET.SubElement(root, "mxCell", 
                                    id=cell_id, 
                                    style=style, 
                                    parent=parent_id, 
                                    vertex="1")
            
            x_pos, y_pos = node_positions.get(original_i, (filtered_i * 180, 1500))
            if page_info['mode'] in ('components', 'flow'):
                width, height = ('160', '90')
            elif page_info['mode'] == 'network' and not is_network_container and parent_id != '1':
                width, height = ('150', '80')
            else:
                width, height = ('60', '60') if parent_id != '1' else ('80', '80')
            
            ET.SubElement(node_cell, "mxGeometry", 
                         attrib={'x': str(x_pos), 'y': str(y_pos), 
                                'width': width, 'height': height, 'as': 'geometry'})
            
            object_attribs = {'label': f"<b>{item.get('name', 'N/A')}</b>", 
                             'as': 'value', 'type': str(item.get('type', ''))}
            if page_info['mode'] == 'components' and item.get('resourceGroup'):
                object_attribs['label'] += f"<br><font style=\"font-size:9px;color:#666666\">RG: {item['resourceGroup']}</font>"
            if embed_data:
                for key, value in item.items():
                    if key not in ['type', 'name']:
                        object_attribs[key.replace(':', '_')] = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            ET.SubElement(node_cell, "object", attrib=object_attribs)
        
        # Crear dependencias (flechas) según el modo de la página
        edges_to_create = []
        
        if page_info['mode'] == 'infrastructure' and tree_edges:
            # Usar conexiones del árbol jerárquico
            print(f"🔗 Página {page_info['name']}: Usando {len(tree_edges)} conexiones de árbol jerárquico")
            item_id_to_idx = {}
            for filtered_i, (original_i, item) in enumerate(items_to_render):
                item_id_to_idx[item['id'].lower()] = filtered_i
            
            for child_id, parent_id in tree_edges:
                if child_id in item_id_to_idx and parent_id in item_id_to_idx:
                    edges_to_create.append((child_id, parent_id))
        else:
            # Para otros modos, determinar dependencias según las opciones
            if page_info['mode'] == 'network' and use_no_hierarchy_edges:
                print(f"🔗 Página {page_info['name']}: Filtrando enlaces jerárquicos de {len(dependencies)} dependencias")
                
                # Crear diccionario de mapeo ID → tipo usando solo elementos filtrados
                id_to_type = {}
                for filtered_i, (original_i, item) in enumerate(items_to_render):
                    id_to_type[item['id'].lower()] = item.get('type', '').lower()
                
                for src_id, tgt_id in dependencies:
                    source_type = id_to_type.get(src_id.lower(), '')
                    target_type = id_to_type.get(tgt_id.lower(), '')
                    
                    if source_type and target_type:
                        # Excluir enlaces jerárquicos
                        has_rg_involvement = (
                            source_type == 'microsoft.resources/subscriptions/resourcegroups' or 
                            target_type == 'microsoft.resources/subscriptions/resourcegroups'
                        )
                        
                        is_vnet_subnet_link = (
                            (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/virtualnetworks/subnets') or
                            (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/virtualnetworks')
                        )
                        
                        network_hierarchy_patterns = [
                            (source_type == 'microsoft.network/privateendpoints' and target_type == 'microsoft.network/virtualnetworks'),
                            (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/privateendpoints'),
                            (source_type == 'microsoft.network/privateendpoints' and target_type == 'microsoft.network/virtualnetworks/subnets'),
                            (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/privateendpoints'),
                            (source_type == 'microsoft.network/networkinterfaces' and target_type == 'microsoft.network/virtualnetworks'),
                            (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/networkinterfaces'),
                            (source_type == 'microsoft.network/networkinterfaces' and target_type == 'microsoft.network/virtualnetworks/subnets'),
                            (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/networkinterfaces'),
                            (source_type == 'microsoft.network/privatednszones/virtualnetworklinks' and target_type == 'microsoft.network/virtualnetworks'),
                            (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/privatednszones/virtualnetworklinks'),
                        ]
                        
                        is_network_hierarchy_link = any(network_hierarchy_patterns)
                        
                        if not has_rg_involvement and not is_vnet_subnet_link and not is_network_hierarchy_link:
                            edges_to_create.append((src_id, tgt_id))
                
                print(f"🔗 Página {page_info['name']}: Conservando {len(edges_to_create)} enlaces de dependencias")
            elif page_info['mode'] == 'components':
                from drawio.filtering import filter_governance_dependencies
                edges_to_create = filter_governance_dependencies(dependencies, items)
                print(f"🔗 Página {page_info['name']}: {len(edges_to_create)} relaciones de integración (sin membresía MG/Subscription/RG)")
            else:
                # Usar dependencias originales
                edges_to_create = dependencies
        
        # Agregar dependencias no jerárquicas para modo infrastructure
        if page_info['mode'] == 'infrastructure':
            print(f"🔗 Página {page_info['name']}: Agregando {len(dependencies)} dependencias adicionales")
            hierarchical_pairs = set(tree_edges) if tree_edges else set()
            
            for src_id, tgt_id in dependencies:
                dependency_pair = (src_id.lower(), tgt_id.lower())
                reverse_pair = (tgt_id.lower(), src_id.lower())
                
                if dependency_pair not in hierarchical_pairs and reverse_pair not in hierarchical_pairs:
                    edges_to_create.append((src_id, tgt_id))
        
        # Crear las flechas
        edge_counter = 0
        for source_id, target_id in edges_to_create:
            source_id_lower = source_id.lower()
            target_id_lower = target_id.lower()
            
            if source_id_lower in azure_id_to_cell_id and target_id_lower in azure_id_to_cell_id:
                source_cell = azure_id_to_cell_id[source_id_lower]
                target_cell = azure_id_to_cell_id[target_id_lower]
                
                # Determinar estilo de la flecha
                is_hierarchical = False
                is_rg_to_subscription = False
                is_resource_to_rg = False
                is_vnet_peering = False

                # Detectar peering entre VNets
                source_item = next((item for item in items if item['id'].lower() == source_id_lower), None)
                target_item = next((item for item in items if item['id'].lower() == target_id_lower), None)
                
                if source_item and target_item:
                    source_type = source_item.get('type', '').lower()
                    target_type = target_item.get('type', '').lower()
                    
                    # Es peering si ambos son VNets
                    if (source_type == 'microsoft.network/virtualnetworks' and 
                        target_type == 'microsoft.network/virtualnetworks'):
                        is_vnet_peering = True

                if page_info['mode'] == 'infrastructure' and tree_edges:
                    is_hierarchical = (source_id.lower(), target_id.lower()) in [(c.lower(), p.lower()) for c, p in tree_edges]
                    
                    if is_hierarchical and source_item and target_item:
                        is_rg_to_subscription = (source_type == 'microsoft.resources/subscriptions/resourcegroups' and
                                                 target_type == 'microsoft.resources/subscriptions')

                        is_resource_to_rg = (target_type == 'microsoft.resources/subscriptions/resourcegroups' and 
                                           source_type not in ['microsoft.management/managementgroups', 
                                                             'microsoft.resources/subscriptions',
                                                             'microsoft.resources/subscriptions/resourcegroups'])
                
                # Estilos específicos con VNet peering en primer lugar
                if is_vnet_peering:
                    style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#FF6B35;strokeWidth=3;dashed=0;"
                elif is_hierarchical and is_rg_to_subscription:
                    style = "edgeStyle=entityRelationEdgeStyle;exitX=0.5;exitY=0;exitPerimeter=1;entryX=0.5;entryY=1;entryPerimeter=1;rounded=0;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
                elif is_hierarchical and is_resource_to_rg:
                    style = "edgeStyle=straight;rounded=0;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
                elif is_hierarchical:
                    style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
                else:
                    style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#757575;strokeWidth=1;dashed=1;"
                
                edge_label = ""
                if page_info['mode'] in ('components', 'network') and source_item and target_item:
                    from drawio.edge_labels import describe_relationship
                    edge_label = describe_relationship(source_type, target_type)
                
                edge_cell = ET.SubElement(root, "mxCell", 
                                        id=f"edge-{page_info['id']}-{edge_counter}", 
                                        value=edge_label,
                                        style=style, 
                                        parent="1", 
                                        edge="1", 
                                        source=source_cell, 
                                        target=target_cell)
                ET.SubElement(edge_cell, "mxGeometry", attrib={'relative': '1', 'as': 'geometry'})
                edge_counter += 1
    
    print("✅ Archivo multipágina generado exitosamente")
    return pretty_print_xml_wrapper(mxfile)

def generate_drawio_file(items, dependencies, embed_data=True, include_ids=None, diagram_mode='infrastructure', no_hierarchy_edges=False):
    """
    Función principal para generar archivos draw.io
    """
    # Si el modo es 'all', generar archivo multipágina
    if diagram_mode == 'all':
        return generate_drawio_multipage_file(items, dependencies, embed_data, include_ids, no_hierarchy_edges)

    # El modo 'hld' agrega recursos por Resource Group (no es 1 nodo por recurso
    # como el resto de modos), así que genera su propio XML de forma autónoma.
    if diagram_mode == 'hld':
        try:
            from drawio.layouts.hld import generate_hld_diagram_xml
        except ImportError:
            from .drawio.layouts.hld import generate_hld_diagram_xml
        return generate_hld_diagram_xml(items, dependencies, embed_data)
    
    # Para otros modos, usar la función original
    import sys
    import json
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    print("INFO: Generando el archivo .drawio...")
    
    # Establecer nombre de página según el modo del diagrama
    page_names = {
        'infrastructure': 'Infrastructure',
        'network': 'Network',
        'components': 'Components',
        'flow': 'Flow',
        'lld': 'LLD'
    }
    page_name = page_names.get(diagram_mode, 'Azure Infrastructure')
    
    mxfile = ET.Element("mxfile", host="app.diagrams.net", agent="python-script")
    diagram = ET.SubElement(mxfile, "diagram", id="main-diagram", name=page_name)
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel", dx="2500", dy="2000", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="4681", pageHeight="3300")
    root = ET.SubElement(mxGraphModel, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    azure_id_to_cell_id = {}
    levels = {0: [], 1: [], 2: [], 3: []}
    mg_id_to_idx, sub_id_to_idx, rg_id_to_idx = {}, {}, {}
    for i, item in enumerate(items):
        t = (item.get('type') or '').lower()
        if t == 'microsoft.management/managementgroups': levels[0].append((i, item)); mg_id_to_idx[item['id'].lower()] = i
        elif t == 'microsoft.resources/subscriptions': levels[1].append((i, item)); sub_id_to_idx[item['id'].lower()] = i
        elif t == 'microsoft.resources/subscriptions/resourcegroups': levels[2].append((i, item)); rg_id_to_idx[item['id'].lower()] = i
        else: levels[3].append((i, item))

    node_positions, group_info, resource_to_parent_id = {}, [], {}
    tree_edges = []  # Para almacenar las conexiones del árbol
    extended_items = items  # Por defecto, usar items originales
    
    if diagram_mode in ('network', 'lld'):
        extended_items, node_positions, group_info, resource_to_parent_id = generate_network_layout_wrapper(items, dependencies)
    elif diagram_mode == 'components':
        node_positions = generate_components_layout_wrapper(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)
    elif diagram_mode == 'flow':
        node_positions, group_info, resource_to_parent_id = generate_flow_layout_wrapper(items, dependencies)
    else: # 'infrastructure'
        node_positions, group_info, resource_to_parent_id, tree_edges = generate_infrastructure_layout_wrapper(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx)

    # Fallback de posicionamiento para nodos sin posición
    for i, item in enumerate(extended_items):
        if i not in node_positions:
            node_positions[i] = ((i % 15) * 180, 1500 + (i // 15) * 150)

    # Crear agrupadores (contenedores)
    for group in group_info:
        group_cell = ET.SubElement(root, "mxCell", id=group['id'], style=group['style'], parent=group.get('parent_id', '1'), vertex="1")
        ET.SubElement(group_cell, "mxGeometry", attrib={'x': str(group['x']), 'y': str(group['y']), 'width': str(group['width']), 'height': str(group['height']), 'as': 'geometry'})
        ET.SubElement(group_cell, "object", attrib={'label': group['label'], 'as': 'value'})

    # Preparar lista de elementos a renderizar (filtrando Management Groups en modo network,
    # y elementos de gobierno -MG/Subscription/RG- en modo components)
    items_to_render = []
    original_to_filtered_index = {}
    
    for i, item in enumerate(extended_items):
        resource_type_lower = (item.get('type') or '').lower()
        
        # Filtrar Management Groups en modo network/lld
        if diagram_mode in ('network', 'lld') and resource_type_lower == 'microsoft.management/managementgroups':
            continue  # Saltear Management Groups en modo network
        
        # Filtrar elementos de gobierno en modo components/flow (no son "tecnología a implementar")
        if diagram_mode in ('components', 'flow'):
            from drawio.filtering import GOVERNANCE_TYPES
            if resource_type_lower in GOVERNANCE_TYPES:
                continue
        
        # Mapear índice original al filtrado
        filtered_index = len(items_to_render)
        original_to_filtered_index[i] = filtered_index
        items_to_render.append((i, item))

    # Crear nodos de recursos
    for filtered_i, (original_i, item) in enumerate(items_to_render):
        cell_id = f"node-{filtered_i}"
        azure_id_to_cell_id[item['id'].lower()] = cell_id
        style = get_node_style_wrapper(item.get('type'))
        
        # En modo network/lld, ajustar estilo para RG, VNet y Subnet para mostrar texto a la derecha
        is_network_container = False
        if diagram_mode in ('network', 'lld'):
            resource_type_lower = (item.get('type') or '').lower()
            if resource_type_lower in ['microsoft.resources/subscriptions/resourcegroups', 
                                     'microsoft.network/virtualnetworks', 
                                     'microsoft.network/virtualnetworks/subnets']:
                is_network_container = True
                # Cambiar estilo para mostrar texto a la derecha del icono
                if 'image=' in style:
                    style = style.replace('align=center', 'align=left;labelPosition=right;verticalLabelPosition=middle;verticalAlign=middle')
            elif 'whiteSpace=wrap' not in style:
                # Recursos individuales (NICs, Private Endpoints, etc.) pueden tener
                # nombres muy largos; sin wrap invaden a sus vecinos en el grid.
                if not style.endswith(';'):
                    style += ';'
                style += 'whiteSpace=wrap;'
        
        # En modo components, permitir que la etiqueta haga wrap dentro de su columna
        # en vez de invadir los nodos vecinos (nombres de Azure pueden ser muy largos).
        if diagram_mode in ('components', 'flow') and 'whiteSpace=wrap' not in style:
            if not style.endswith(';'):
                style += ';'
            style += 'whiteSpace=wrap;'
        
        parent_id = resource_to_parent_id.get(original_i, '1')
        
        node_cell = ET.SubElement(root, "mxCell", id=cell_id, style=style, parent=parent_id, vertex="1")
        
        x_pos, y_pos = node_positions.get(original_i)
        if diagram_mode in ('components', 'flow'):
            width, height = ('160', '90')
        elif diagram_mode == 'lld' and not is_network_container and parent_id != '1':
            width, height = ('150', '100')  # más alto que network: ficha técnica de 2 líneas (SKU/ubicación + tags)
        elif diagram_mode == 'network' and not is_network_container and parent_id != '1':
            width, height = ('150', '80')
        else:
            width, height = ('60', '60') if parent_id != '1' else ('80', '80')
        
        ET.SubElement(node_cell, "mxGeometry", attrib={'x': str(x_pos), 'y': str(y_pos), 'width': width, 'height': height, 'as': 'geometry'})
        
        object_attribs = {'label': f"<b>{item.get('name', 'N/A')}</b>", 'as': 'value', 'type': str(item.get('type', ''))}
        if diagram_mode == 'components' and item.get('resourceGroup'):
            object_attribs['label'] += f"<br><font style=\"font-size:9px;color:#666666\">RG: {item['resourceGroup']}</font>"
        if diagram_mode == 'lld' and not is_network_container:
            from drawio.resource_spec import describe_resource_spec, describe_resource_tags
            spec = describe_resource_spec(item)
            if spec:
                object_attribs['label'] += f"<br><font style=\"font-size:9px;color:#666666\">{spec}</font>"
            tags = describe_resource_tags(item)
            if tags:
                object_attribs['label'] += f"<br><font style=\"font-size:8px;color:#8a8a8a\">🏷 {tags}</font>"
        if embed_data:
            for key, value in item.items():
                if key not in ['type', 'name']:
                    object_attribs[key.replace(':', '_')] = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        ET.SubElement(node_cell, "object", attrib=object_attribs)

    # Crear dependencias (flechas)
    edges_to_create = []
    
    if diagram_mode == 'infrastructure' and tree_edges:
        edges_to_create.extend(tree_edges)
        
        # Agregar dependencias no jerárquicas
        hierarchical_pairs = set(tree_edges)
        for src_id, tgt_id in dependencies:
            if (src_id, tgt_id) not in hierarchical_pairs and (tgt_id, src_id) not in hierarchical_pairs:
                edges_to_create.append((src_id, tgt_id))
    elif diagram_mode in ('network', 'lld') and no_hierarchy_edges:
        print(f"🔗 Filtrando enlaces jerárquicos de {len(dependencies)} dependencias")
        
        # Crear diccionario de mapeo ID → tipo
        id_to_type = {item['id'].lower(): item.get('type', '').lower() for original_i, item in items_to_render}
        
        for src_id, tgt_id in dependencies:
            source_type = id_to_type.get(src_id.lower(), '')
            target_type = id_to_type.get(tgt_id.lower(), '')
            
            if source_type and target_type:
                # Excluir enlaces jerárquicos
                has_rg_involvement = (
                    source_type == 'microsoft.resources/subscriptions/resourcegroups' or 
                    target_type == 'microsoft.resources/subscriptions/resourcegroups'
                )
                
                is_vnet_subnet_link = (
                    (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/virtualnetworks/subnets') or
                    (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/virtualnetworks')
                )
                
                network_hierarchy_patterns = [
                    (source_type == 'microsoft.network/privateendpoints' and target_type == 'microsoft.network/virtualnetworks'),
                    (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/privateendpoints'),
                    (source_type == 'microsoft.network/privateendpoints' and target_type == 'microsoft.network/virtualnetworks/subnets'),
                    (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/privateendpoints'),
                    (source_type == 'microsoft.network/networkinterfaces' and target_type == 'microsoft.network/virtualnetworks'),
                    (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/networkinterfaces'),
                    (source_type == 'microsoft.network/networkinterfaces' and target_type == 'microsoft.network/virtualnetworks/subnets'),
                    (source_type == 'microsoft.network/virtualnetworks/subnets' and target_type == 'microsoft.network/networkinterfaces'),
                    (source_type == 'microsoft.network/privatednszones/virtualnetworklinks' and target_type == 'microsoft.network/virtualnetworks'),
                    (source_type == 'microsoft.network/virtualnetworks' and target_type == 'microsoft.network/privatednszones/virtualnetworklinks'),
                ]
                
                is_network_hierarchy_link = any(network_hierarchy_patterns)
                
                if not has_rg_involvement and not is_vnet_subnet_link and not is_network_hierarchy_link:
                    edges_to_create.append((src_id, tgt_id))
        
        print(f"🔗 Conservando {len(edges_to_create)} enlaces de dependencias")
    elif diagram_mode == 'components':
        from drawio.filtering import filter_governance_dependencies
        edges_to_create = filter_governance_dependencies(dependencies, items)
        print(f"🔗 {len(edges_to_create)} relaciones de integración (sin membresía MG/Subscription/RG)")
    elif diagram_mode == 'flow':
        from drawio.filtering import filter_flow_dependencies
        edges_to_create = filter_flow_dependencies(dependencies, items)
        print(f"🔗 {len(edges_to_create)} relaciones de integración en el flujo")
    else:
        edges_to_create = dependencies
    
    edge_counter = 0
    for source_id, target_id in edges_to_create:
        source_id_lower = source_id.lower()
        target_id_lower = target_id.lower()
        
        if source_id_lower in azure_id_to_cell_id and target_id_lower in azure_id_to_cell_id:
            source_cell = azure_id_to_cell_id[source_id_lower]
            target_cell = azure_id_to_cell_id[target_id_lower]
            
            is_hierarchical = (source_id, target_id) in tree_edges if tree_edges else False
            is_rg_to_subscription = False
            is_resource_to_rg = False
            is_vnet_peering = False

            # Obtener items para clasificar la conexión
            source_item = next((item for original_i, item in items_to_render if item['id'].lower() == source_id_lower), None)
            target_item = next((item for original_i, item in items_to_render if item['id'].lower() == target_id_lower), None)
            
            # Detectar peering entre VNets
            if source_item and target_item:
                source_type = source_item.get('type', '').lower()
                target_type = target_item.get('type', '').lower()
                
                # Es peering si ambos son VNets
                if (source_type == 'microsoft.network/virtualnetworks' and 
                    target_type == 'microsoft.network/virtualnetworks'):
                    is_vnet_peering = True

            if is_hierarchical and source_item and target_item:
                is_rg_to_subscription = (source_type == 'microsoft.resources/subscriptions/resourcegroups' and
                                         target_type == 'microsoft.resources/subscriptions')
                is_resource_to_rg = (target_type == 'microsoft.resources/subscriptions/resourcegroups' and 
                                   source_type not in ['microsoft.management/managementgroups', 
                                                     'microsoft.resources/subscriptions',
                                                     'microsoft.resources/subscriptions/resourcegroups'])

            # Estilos específicos con VNet peering en primer lugar
            if is_vnet_peering:
                style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#FF6B35;strokeWidth=3;dashed=0;"
            elif is_hierarchical and is_rg_to_subscription:
                style = "edgeStyle=entityRelationEdgeStyle;exitX=0.5;exitY=0;exitPerimeter=1;entryX=0.5;entryY=1;entryPerimeter=1;rounded=0;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
            elif is_hierarchical and is_resource_to_rg:
                style = "edgeStyle=straight;rounded=0;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
            elif is_hierarchical:
                style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
            elif diagram_mode == 'flow':
                style = ("edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
                         "endArrow=classic;strokeColor=#1976d2;strokeWidth=2;dashed=0;"
                         "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
            else:
                style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#757575;strokeWidth=1;dashed=1;"
            
            edge_label = ""
            if diagram_mode in ('network', 'flow', 'lld') and source_item and target_item:
                # Las relaciones de mera contención (RG->recurso, cualquier cosa ubicada
                # dentro de una Subnet/VNet) ya se comunican visualmente por el anidado
                # de contenedores; etiquetarlas además con texto ("Subnet"/"VNet") solo
                # produce texto solapado sobre la propia etiqueta del contenedor. Solo se
                # etiquetan relaciones que aportan información no obvia (ej. Private Link,
                # Peering entre VNets).
                subnet_type = 'microsoft.network/virtualnetworks/subnets'
                vnet_type = 'microsoft.network/virtualnetworks'
                is_pure_containment = (
                    source_type == 'microsoft.resources/subscriptions/resourcegroups' or
                    target_type == 'microsoft.resources/subscriptions/resourcegroups' or
                    target_type == subnet_type or
                    (target_type == vnet_type and source_type != vnet_type)
                )
                if not is_pure_containment:
                    from drawio.edge_labels import describe_relationship
                    edge_label = describe_relationship(source_type, target_type)
            
            edge_cell = ET.SubElement(root, "mxCell", 
                                    id=f"edge-{edge_counter}", 
                                    value=edge_label,
                                    style=style, 
                                    parent="1", 
                                    edge="1", 
                                    source=source_cell, 
                                    target=target_cell)
            
            ET.SubElement(edge_cell, "mxGeometry", 
                         attrib={'relative': '1', 'as': 'geometry'})
            
            edge_counter += 1
            
    return pretty_print_xml_wrapper(mxfile)

def filter_items_and_dependencies(items, dependencies, include_ids=None, exclude_ids=None):
    if not include_ids and not exclude_ids:
        return items, dependencies
    include_ids = set(i.lower() for i in include_ids) if include_ids else None
    exclude_ids = set(i.lower() for i in exclude_ids) if exclude_ids else set()
    child_map = {}
    for src, tgt in dependencies:
        child_map.setdefault(tgt.lower(), set()).add(src.lower())
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
    if include_ids:
        # Un recurso puede quedar seleccionado por depender (indirectamente) de otro
        # recurso en una Resource Group distinta a la de origen (ej. arquitectura
        # hub-spoke: un Private Endpoint de otra RG apunta a la subnet del hub). En
        # ese caso, el propio objeto "Resource Group" de esa RG vecina no tiene por
        # qué estar entre los descendientes recolectados, aunque sí queramos poder
        # dibujar su contenedor con nombre en los modos 'network'/'lld'. Se añade
        # aquí explícitamente el Resource Group de cada recurso ya seleccionado.
        rg_ids_needed = set()
        for item in items:
            if item['id'].lower() in selected_ids:
                rg, sub = item.get('resourceGroup'), item.get('subscriptionId')
                if rg and sub:
                    rg_ids_needed.add(f"/subscriptions/{sub}/resourcegroups/{rg}".lower())
        selected_ids.update(rg_ids_needed & all_ids)
    if exclude_ids:
        to_exclude = collect_descendants(exclude_ids)
        to_exclude.update(exclude_ids)
        selected_ids = selected_ids - to_exclude
    filtered_items = [item for item in items if item['id'].lower() in selected_ids]
    filtered_dependencies = [(src, tgt) for src, tgt in dependencies if src.lower() in selected_ids and tgt.lower() in selected_ids]
    return filtered_items, filtered_dependencies

"""
Generador del diagrama HLD (High-Level Design).

Referencia: guía de Microsoft Well-Architected Framework sobre diagramas de
arquitectura (Context diagram + High-level system/container diagram):
https://learn.microsoft.com/azure/well-architected/architect-role/design-diagrams

Un HLD es una vista abstraída pensada para stakeholders/arquitectos que
necesitan entender "qué hay desplegado y cómo se relacionan las piezas a
alto nivel", sin el ruido técnico de cada NIC o Private Endpoint. Por eso,
en vez de un nodo por recurso (como 'components'/'network'/'lld'), este modo
agrega los recursos en un único bloque por Resource Group, con un recuento
por categoría funcional (reutilizando la misma clasificación que 'components'
vía `classify_component_category`), y colapsa las relaciones entre recursos
en una única flecha por par de Resource Groups relacionados.

Al ser una agregación (N recursos -> 1 bloque por RG), este modo no encaja en
el pipeline genérico de nodo-por-item de drawio_export.py: genera su propio
XML completo de forma autónoma.
"""

import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

from .utils import classify_component_category, extract_resource_name, COMPONENT_CATEGORIES
from ..icons import AZURE_ICONS

BLOCK_WIDTH = 260
BLOCK_HEADER_HEIGHT = 36
BLOCK_LINE_HEIGHT = 22
BLOCK_MIN_HEIGHT = 70
BLOCK_PADDING_BOTTOM = 12
CATEGORY_ICON_SIZE = 16
GAP_X = 80
GAP_Y = 70
BLOCKS_PER_ROW = 3
SUB_PADDING = {'left': 30, 'top': 50, 'right': 30, 'bottom': 30}
SUB_GAP_Y = 60

RG_BLOCK_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff8e1;strokeColor=#d6b656;"
    "fontSize=13;fontStyle=1;align=left;verticalAlign=top;spacingLeft=14;spacingTop=10;"
    "arcSize=6;"
)
SUB_CONTAINER_STYLE = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"
    "fontSize=14;fontStyle=1;align=left;verticalAlign=top;spacingLeft=15;spacingTop=10;"
    "container=1;"
)
EDGE_STYLE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
    "endArrow=classic;strokeColor=#1976d2;strokeWidth=2;fontSize=11;fontStyle=1;"
)
CATEGORY_ICON_STYLE = "image;aspect=fixed;html=1;points=[];image={icon};"

# Un tipo de recurso representativo por categoría, para mostrar su icono oficial
# de Azure (el artículo de referencia pide explícitamente "Azure service icons",
# no emojis genéricos) junto al recuento de esa categoría dentro de cada RG.
CATEGORY_REPRESENTATIVE_TYPE = {
    'Compute': 'microsoft.compute/virtualmachines',
    'Storage': 'microsoft.storage/storageaccounts',
    'Network': 'microsoft.network/virtualnetworks',
    'Database': 'microsoft.sql/servers',
    'Analytics': 'microsoft.synapse/workspaces',
    'IoT': 'microsoft.devices/iothubs',
    'Security': 'microsoft.keyvault/vaults',
    'AI/ML': 'microsoft.cognitiveservices/accounts',
    'Management': 'microsoft.operationalinsights/workspaces',
    'Media': 'microsoft.media/mediaservices',
    'Other': None,
}


def _resource_group_key(item):
    """ID (lowercase) del resource group de un item, o None si no aplica."""
    rg = item.get('resourceGroup')
    if rg:
        sub_id = item.get('subscriptionId') or ''
        return f"/subscriptions/{sub_id}/resourcegroups/{rg}".lower()
    return None


def _build_rg_summaries(items):
    """
    Agrupa items por Resource Group, devolviendo por cada uno: nombre,
    suscripción, y recuento de recursos por categoría funcional.
    """
    rg_data = {}  # rg_key -> {'name':, 'subscription_id':, 'counts': Counter, 'item_ids': set}
    item_id_to_rg = {}

    for item in items:
        category = classify_component_category(item.get('type'))
        if category is None:
            continue  # Recursos de gobierno (MG/Subscription/RG) no forman parte del bloque
        rg_key = _resource_group_key(item)
        if not rg_key:
            continue
        entry = rg_data.setdefault(rg_key, {
            'name': item.get('resourceGroup'),
            'subscription_id': item.get('subscriptionId'),
            'location': item.get('location'),
            'counts': Counter(),
        })
        entry['counts'][category] += 1
        item_id_to_rg[item['id'].lower()] = rg_key

    return rg_data, item_id_to_rg


def _rg_cross_edges(dependencies, item_id_to_rg):
    """Cuenta relaciones entre pares de Resource Groups distintos."""
    counts = Counter()
    for src, tgt in dependencies:
        src_rg = item_id_to_rg.get(src.lower())
        tgt_rg = item_id_to_rg.get(tgt.lower())
        if src_rg and tgt_rg and src_rg != tgt_rg:
            counts[(src_rg, tgt_rg)] += 1
    return counts


def _block_height(counts):
    lines = sum(1 for c in COMPONENT_CATEGORIES if counts.get(c))
    return max(BLOCK_MIN_HEIGHT, BLOCK_HEADER_HEIGHT + lines * BLOCK_LINE_HEIGHT + BLOCK_PADDING_BOTTOM)


def generate_hld_diagram_xml(items, dependencies, embed_data=True):
    """
    Genera el XML completo (<mxfile>) de un diagrama HLD de una sola página.
    """
    rg_data, item_id_to_rg = _build_rg_summaries(items)
    cross_edges = _rg_cross_edges(dependencies, item_id_to_rg)

    mxfile = ET.Element("mxfile", host="app.diagrams.net", agent="python-script")
    diagram = ET.SubElement(mxfile, "diagram", id="main-diagram", name="HLD")
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel", dx="2500", dy="2000", grid="1", gridSize="10",
                                  guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1",
                                  pageScale="1", pageWidth="4681", pageHeight="3300")
    root = ET.SubElement(mxGraphModel, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    if not rg_data:
        print("⚠️  HLD: no se encontraron recursos agrupables por Resource Group")
        return _pretty_print(mxfile)

    # Agrupar Resource Groups por suscripción para crear swimlanes si hay más de una
    by_subscription = defaultdict(list)
    for rg_key, data in rg_data.items():
        by_subscription[data['subscription_id'] or 'unknown'].append((rg_key, data))

    rg_cell_id = {}
    cursor_y = 40
    multi_sub = len(by_subscription) > 1

    for sub_id, rg_list in sorted(by_subscription.items()):
        rg_list.sort(key=lambda pair: pair[1]['name'] or '')
        rows = [rg_list[i:i + BLOCKS_PER_ROW] for i in range(0, len(rg_list), BLOCKS_PER_ROW)]
        row_heights = [max(_block_height(d['counts']) for _, d in row) for row in rows]
        content_width = BLOCKS_PER_ROW * BLOCK_WIDTH + (BLOCKS_PER_ROW - 1) * GAP_X
        content_height = sum(row_heights) + (len(rows) - 1) * GAP_Y if rows else 0

        parent_id = "1"
        origin_x, origin_y = 40, cursor_y
        if multi_sub:
            sub_container_id = f"hld-sub-{sub_id}"
            sub_width = content_width + SUB_PADDING['left'] + SUB_PADDING['right']
            sub_height = content_height + SUB_PADDING['top'] + SUB_PADDING['bottom']
            sub_cell = ET.SubElement(root, "mxCell", id=sub_container_id, style=SUB_CONTAINER_STYLE,
                                      parent="1", vertex="1")
            ET.SubElement(sub_cell, "mxGeometry", attrib={
                'x': str(origin_x), 'y': str(origin_y),
                'width': str(sub_width), 'height': str(sub_height), 'as': 'geometry'})
            ET.SubElement(sub_cell, "object", attrib={
                'label': f"Suscripción: {sub_id}", 'as': 'value'})
            parent_id = sub_container_id
            block_origin_x, block_origin_y = SUB_PADDING['left'], SUB_PADDING['top']
            cursor_y += sub_height + SUB_GAP_Y
        else:
            block_origin_x, block_origin_y = origin_x, origin_y
            cursor_y += content_height + SUB_GAP_Y

        row_y = block_origin_y
        for row, row_height in zip(rows, row_heights):
            row_x = block_origin_x
            for rg_key, data in row:
                cell_id = f"hld-rg-{len(rg_cell_id)}"
                rg_cell_id[rg_key] = cell_id
                height = _block_height(data['counts'])
                active_categories = [c for c in COMPONENT_CATEGORIES if data['counts'].get(c)]
                label_lines = [f"<b>{data['name']}</b>"]
                for category in active_categories:
                    count = data['counts'][category]
                    # Espacio en blanco a la izquierda del texto para dejar sitio al
                    # icono real de Azure que se dibuja encima como celda aparte.
                    label_lines.append(f"&#160;&#160;&#160;&#160;&#160;{category}: {count}")
                label = "<br>".join(label_lines)

                block_cell = ET.SubElement(root, "mxCell", id=cell_id, style=RG_BLOCK_STYLE,
                                            parent=parent_id, vertex="1")
                ET.SubElement(block_cell, "mxGeometry", attrib={
                    'x': str(row_x), 'y': str(row_y),
                    'width': str(BLOCK_WIDTH), 'height': str(height), 'as': 'geometry'})
                object_attribs = {'label': label, 'as': 'value', 'type': 'hld-resource-group-summary'}
                if embed_data:
                    total = sum(data['counts'].values())
                    object_attribs['resourceGroup'] = str(data['name'])
                    object_attribs['subscriptionId'] = str(data['subscription_id'])
                    object_attribs['totalResources'] = str(total)
                ET.SubElement(block_cell, "object", attrib=object_attribs)

                for line_index, category in enumerate(active_categories):
                    icon_type = CATEGORY_REPRESENTATIVE_TYPE.get(category)
                    icon_path = AZURE_ICONS.get(icon_type) if icon_type else None
                    if not icon_path:
                        continue
                    icon_cell = ET.SubElement(root, "mxCell", id=f"{cell_id}-icon-{line_index}",
                                              style=CATEGORY_ICON_STYLE.format(icon=icon_path),
                                              parent=parent_id, vertex="1")
                    icon_y = row_y + BLOCK_HEADER_HEIGHT + line_index * BLOCK_LINE_HEIGHT + 3
                    ET.SubElement(icon_cell, "mxGeometry", attrib={
                        'x': str(row_x + 6), 'y': str(icon_y),
                        'width': str(CATEGORY_ICON_SIZE), 'height': str(CATEGORY_ICON_SIZE), 'as': 'geometry'})

                row_x += BLOCK_WIDTH + GAP_X
            row_y += row_height + GAP_Y

    # Relaciones agregadas entre Resource Groups
    edge_counter = 0
    for (src_rg, tgt_rg), count in cross_edges.items():
        if src_rg not in rg_cell_id or tgt_rg not in rg_cell_id:
            continue
        edge_cell = ET.SubElement(root, "mxCell", id=f"hld-edge-{edge_counter}",
                                   value=f"{count} relaciones" if count > 1 else "1 relación",
                                   style=EDGE_STYLE, parent="1", edge="1",
                                   source=rg_cell_id[src_rg], target=rg_cell_id[tgt_rg])
        ET.SubElement(edge_cell, "mxGeometry", attrib={'relative': '1', 'as': 'geometry'})
        edge_counter += 1

    print(f"✅ HLD: {len(rg_data)} Resource Groups, {edge_counter} relaciones agregadas entre ellos")
    return _pretty_print(mxfile)


def _pretty_print(mxfile):
    from xml.dom import minidom
    rough_string = ET.tostring(mxfile, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

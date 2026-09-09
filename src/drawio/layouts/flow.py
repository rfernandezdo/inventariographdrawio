"""
Layout de flujo de dependencias (izquierda -> derecha) para diagramas de
arquitectura acotados (pensado para un alcance pequeno, ej. un solo Resource
Group filtrado con --include-ids).

Convencion: cada dependencia (A, B) en `dependencies` significa "A depende de
B" (A usa/necesita B). El layout coloca A a la izquierda de B -la flecha
apunta hacia la derecha, del consumidor hacia el recurso del que depende-
calculando la posicion de cada nodo con el algoritmo estandar de "layering"
de grafos dirigidos aciclicos (longest-path-from-source, tecnica de Sugiyama
simplificada), mas una pasada de reordenamiento "barycenter" dentro de cada
capa para reducir cruces de lineas.

No inventa relaciones: solo usa las dependencias reales ya detectadas por
azure_api.find_dependencies(), filtradas con filter_flow_dependencies() para
excluir membresia organizativa (MG/Subscription/Resource Group) y contencion
VNet<->Subnet, que no son "integraciones tecnologicas" sino jerarquia.
"""

from ..filtering import filter_flow_dependencies, GOVERNANCE_TYPES

LAYER_SPACING_X = 260
NODE_SPACING_Y = 170
NODE_SIZE = 160
TOP_PADDING = 80
LEFT_PADDING = 60
ISOLATED_ROW_GAP = 170

CONTAINER_STYLE_RG = (
    "container=0;rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#90A4AE;"
    "dashed=1;dashPattern=8 4;fontSize=13;fontStyle=2;align=left;verticalAlign=top;"
    "spacingLeft=12;spacingTop=8;"
)


def _build_predecessor_map(item_ids, dependencies):
    """predecessors[v] = nodos u tales que (u, v) es una dependencia (u depende de v)."""
    predecessors = {item_id: [] for item_id in item_ids}
    successors = {item_id: [] for item_id in item_ids}
    for src, tgt in dependencies:
        s, t = src.lower(), tgt.lower()
        if s in predecessors and t in predecessors:
            predecessors[t].append(s)
            successors[s].append(t)
    return predecessors, successors


def _compute_layers(item_ids, predecessors):
    """Calcula el 'layer' (profundidad) de cada nodo via longest-path-from-source."""
    memo = {}

    def layer_of(node, visiting):
        if node in memo:
            return memo[node]
        if node in visiting:
            memo[node] = 0  # ciclo defensivo; no deberia ocurrir con datos reales
            return 0
        preds = predecessors.get(node, [])
        if not preds:
            memo[node] = 0
            return 0
        visiting.add(node)
        result = 1 + max(layer_of(p, visiting) for p in preds)
        visiting.discard(node)
        memo[node] = result
        return result

    for node in item_ids:
        layer_of(node, set())
    return memo


def _order_by_barycenter(layers_nodes, predecessors, order_index):
    """Reordena cada capa (excepto la 0) segun la posicion media de sus predecesores
    en la capa anterior, para reducir cruces de lineas (heuristica barycenter)."""
    for layer_num in sorted(layers_nodes.keys()):
        if layer_num == 0:
            continue
        nodes = layers_nodes[layer_num]

        def barycenter(node):
            positions = [order_index.get(p, 0) for p in predecessors.get(node, []) if p in order_index]
            return sum(positions) / len(positions) if positions else order_index.get(node, 0)

        nodes.sort(key=barycenter)
        for i, node in enumerate(nodes):
            order_index[node] = i


def generate_flow_layout(items, dependencies):
    """
    Genera un layout de flujo de dependencias izquierda -> derecha.

    Args:
        items: Lista de recursos de Azure
        dependencies: Lista de dependencias (src_id, tgt_id)

    Returns:
        tuple: (node_positions, group_info, resource_to_parent_id)
    """
    print("Generando layout de flujo de dependencias (izquierda -> derecha)...")

    item_map = {item['id'].lower(): (i, item) for i, item in enumerate(items)}
    renderable_ids = [
        item_id for item_id, (_, item) in item_map.items()
        if (item.get('type') or '').lower() not in GOVERNANCE_TYPES
    ]

    flow_dependencies = filter_flow_dependencies(dependencies, items)
    predecessors, successors = _build_predecessor_map(renderable_ids, flow_dependencies)

    connected_ids = [n for n in renderable_ids if predecessors[n] or successors[n]]
    isolated_ids = [n for n in renderable_ids if not predecessors[n] and not successors[n]]

    layers = _compute_layers(connected_ids, predecessors)

    layers_nodes = {}
    order_index = {}
    for node in sorted(connected_ids, key=lambda n: item_map[n][1].get('name', n)):
        layer_num = layers.get(node, 0)
        layers_nodes.setdefault(layer_num, []).append(node)
    for nodes in layers_nodes.values():
        for i, node in enumerate(nodes):
            order_index[node] = i

    _order_by_barycenter(layers_nodes, predecessors, order_index)

    node_positions = {}
    group_info = []
    resource_to_parent_id = {}

    max_layer = max(layers_nodes.keys()) if layers_nodes else 0
    for layer_num, nodes in layers_nodes.items():
        x = LEFT_PADDING + (max_layer - layer_num) * LAYER_SPACING_X
        ordered_nodes = sorted(nodes, key=lambda n: order_index.get(n, 0))
        for i, node in enumerate(ordered_nodes):
            idx = item_map[node][0]
            y = TOP_PADDING + i * NODE_SPACING_Y
            node_positions[idx] = (x, y)

    # Recursos sin dependencias funcionales: fila aparte debajo del flujo principal
    if isolated_ids:
        max_rows = max((len(nodes) for nodes in layers_nodes.values()), default=1)
        isolated_y = TOP_PADDING + max_rows * NODE_SPACING_Y + ISOLATED_ROW_GAP
        for i, node in enumerate(sorted(isolated_ids, key=lambda n: item_map[n][1].get('name', n))):
            idx = item_map[node][0]
            x = LEFT_PADDING + i * LAYER_SPACING_X
            node_positions[idx] = (x, isolated_y)

    # Si todos los recursos comparten el mismo Resource Group, dibujar un
    # rectangulo discontinuo que los englobe (misma convencion visual usada
    # para las regiones en el modo network).
    resource_groups = {item.get('resourceGroup') for item in items if item.get('resourceGroup')}
    if len(resource_groups) == 1 and node_positions:
        rg_name = next(iter(resource_groups))
        margin = 40
        min_x = min(pos[0] for pos in node_positions.values()) - margin
        min_y = min(pos[1] for pos in node_positions.values()) - margin
        max_x = max(pos[0] for pos in node_positions.values()) + NODE_SIZE + margin
        max_y = max(pos[1] for pos in node_positions.values()) + NODE_SIZE + margin
        group_info.append({
            'id': 'flow_rg_container', 'parent_id': '1', 'type': 'rg_container',
            'x': min_x, 'y': min_y,
            'width': max_x - min_x, 'height': max_y - min_y,
            'label': rg_name, 'style': CONTAINER_STYLE_RG
        })

    print(f"Layout de flujo completado: {len(connected_ids)} recursos en {len(layers_nodes)} capas, "
          f"{len(isolated_ids)} sin dependencias funcionales")
    return node_positions, group_info, resource_to_parent_id

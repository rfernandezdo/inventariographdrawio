# Ejemplos de Código para GitHub Copilot

## Ejemplo 1: Uso Básico de la API

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from drawio_export import generate_drawio_file

# Datos de ejemplo
resources = [
    {
        "id": "/subscriptions/sub-001",
        "name": "Test Subscription",
        "type": "Microsoft.Resources/subscriptions",
        "subscription_id": "sub-001"
    },
    {
        "id": "/subscriptions/sub-001/resourceGroups/rg-web",
        "name": "rg-web",
        "type": "Microsoft.Resources/resourceGroups",
        "subscription_id": "sub-001",
        "location": "eastus"
    },
    {
        "id": "/subscriptions/sub-001/resourceGroups/rg-web/providers/Microsoft.Compute/virtualMachines/vm-web-01",
        "name": "vm-web-01",
        "type": "Microsoft.Compute/virtualMachines",
        "resource_group": "rg-web",
        "subscription_id": "sub-001",
        "location": "eastus"
    }
]

dependencies = []

# Generar diagrama
xml = generate_drawio_file(
    resources, 
    dependencies, 
    embed_data=True, 
    diagram_mode='infrastructure'
)

# Guardar archivo
with open('diagram.drawio', 'w', encoding='utf-8') as f:
    f.write(xml)

print("Diagrama generado: diagram.drawio")
```

## Ejemplo 2: Test de Layout de Arco

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from drawio_export import generate_drawio_file

def test_arc_layout_with_straight_edges():
    """Test que verifica el layout de arco con aristas rectas para RG→Resource"""
    
    # Datos de prueba
    resources = [
        {
            "id": "/subscriptions/sub-001",
            "name": "Test Subscription",
            "type": "Microsoft.Resources/subscriptions",
            "subscription_id": "sub-001"
        },
        {
            "id": "/subscriptions/sub-001/resourceGroups/rg-test",
            "name": "rg-test",
            "type": "Microsoft.Resources/resourceGroups",
            "subscription_id": "sub-001",
            "location": "eastus"
        }
    ]
    
    # Añadir múltiples recursos para forzar layout de arco
    for i in range(1, 6):  # 5 recursos = layout de arco
        resources.append({
            "id": f"/subscriptions/sub-001/resourceGroups/rg-test/providers/Microsoft.Compute/virtualMachines/vm-{i:02d}",
            "name": f"vm-{i:02d}",
            "type": "Microsoft.Compute/virtualMachines",
            "resource_group": "rg-test",
            "subscription_id": "sub-001",
            "location": "eastus"
        })
    
    # Generar diagrama
    xml = generate_drawio_file(resources, [], diagram_mode='infrastructure')
    
    # Analizar XML para verificar estilos de aristas
    root = ET.fromstring(xml)
    straight_edges = 0
    orthogonal_edges = 0
    
    for cell in root.findall(".//mxCell"):
        if cell.get('edge') == '1':
            style = cell.get('style', '')
            if 'edgeStyle=straight' in style:
                straight_edges += 1
            elif 'edgeStyle=orthogonalEdgeStyle' in style:
                orthogonal_edges += 1
    
    print(f"Aristas rectas (RG→Resource): {straight_edges}")
    print(f"Aristas ortogonales (Sub→RG): {orthogonal_edges}")
    
    # Verificaciones
    assert straight_edges >= 5, f"Esperaba ≥5 aristas rectas, encontré {straight_edges}"
    assert orthogonal_edges >= 1, f"Esperaba ≥1 arista ortogonal, encontré {orthogonal_edges}"
    
    # Guardar para inspección visual
    with open('test-arc-layout.drawio', 'w', encoding='utf-8') as f:
        f.write(xml)
    
    print("✅ Test pasó - Layout de arco con aristas correctas")
    return True

if __name__ == "__main__":
    test_arc_layout_with_straight_edges()
```

## Ejemplo 3: Implementación de Nuevo Tipo de Layout

```python
def generate_custom_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """
    Ejemplo de cómo implementar un nuevo tipo de layout
    """
    positions = {}
    edges = []
    
    # 1. Identificar estructura jerárquica
    def is_hierarchical_dependency(src_item, tgt_item):
        src_id = src_item.get('id', '')
        tgt_id = tgt_item.get('id', '')
        
        # Management Group → Subscription
        if (src_id in mg_id_to_idx and tgt_id in sub_id_to_idx):
            return True
        
        # Subscription → Resource Group
        if (is_subscription(src_id) and is_resource_group(tgt_id) and
            src_item.get('subscriptionId') == tgt_item.get('subscription_id')):
            return True
            
        # Resource Group → Resource
        if (is_resource_group(src_id) and not is_resource_group(tgt_id) and
            src_item.get('subscription_id') == tgt_item.get('subscription_id')):
            return True
            
        return False
    
    # 2. Construir árbol jerárquico
    hierarchical_deps = []
    for src_idx, tgt_idx in dependencies:
        src_item = items[src_idx]
        tgt_item = items[tgt_idx]
        
        if is_hierarchical_dependency(src_item, tgt_item):
            hierarchical_deps.append((src_idx, tgt_idx))
    
    # 3. Calcular posiciones usando algoritmo personalizado
    def calculate_positions(node_idx, level=0, x_offset=0):
        item = items[node_idx]
        
        # Posición base
        x = x_offset + level * 300
        y = level * 200
        
        # Aplicar lógica de layout específica
        if is_resource_group(item.get('id', '')):
            # Layout especial para RG
            children = get_children(node_idx)
            if len(children) >= 4:
                # Layout radial personalizado
                x, y = apply_custom_radial_layout(item, children, x, y)
        
        positions[node_idx] = (x, y)
        return x, y
    
    # 4. Aplicar layout recursivamente
    roots = find_root_nodes(hierarchical_deps)
    for root in roots:
        calculate_positions(root)
    
    # 5. Generar aristas con estilos correctos
    for src_idx, tgt_idx in hierarchical_deps:
        src_item = items[src_idx]
        tgt_item = items[tgt_idx]
        
        # Determinar estilo de arista
        if (is_resource_group(src_item.get('id', '')) and 
            not is_resource_group(tgt_item.get('id', ''))):
            # RG → Resource: línea recta
            edge_style = "edgeStyle=straight;rounded=0;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
        else:
            # Otros: línea ortogonal
            edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
        
        edges.append({
            'source': src_idx,
            'target': tgt_idx,
            'style': edge_style
        })
    
    return positions, edges

def apply_custom_radial_layout(rg_item, children, center_x, center_y):
    """Aplicar layout radial personalizado"""
    import math
    
    num_children = len(children)
    radius = max(200, num_children * 40)
    
    # Posicionar RG en el centro
    rg_x = center_x
    rg_y = center_y
    
    # Posicionar recursos en arco hacia abajo
    start_angle = math.pi  # 180°
    end_angle = 0         # 0°
    angle_step = (start_angle - end_angle) / (num_children - 1) if num_children > 1 else 0
    
    for i, child_idx in enumerate(children):
        angle = start_angle - (i * angle_step)
        child_x = rg_x + radius * math.cos(angle)
        child_y = rg_y + radius * math.sin(angle)
        
        positions[child_idx] = (child_x, child_y)
    
    return rg_x, rg_y
```

## Ejemplo 4: Test de Escalabilidad

```python
#!/usr/bin/env python3
def test_large_scale_performance():
    """Test de rendimiento con gran cantidad de recursos"""
    import time
    
    # Generar datos de prueba grandes
    resources = []
    dependencies = []
    
    # 1000 recursos distribuidos en 100 RGs
    for rg_num in range(1, 101):  # 100 RGs
        rg_id = f"/subscriptions/sub-001/resourceGroups/rg-{rg_num:03d}"
        resources.append({
            "id": rg_id,
            "name": f"rg-{rg_num:03d}",
            "type": "Microsoft.Resources/resourceGroups",
            "subscription_id": "sub-001",
            "location": "eastus"
        })
        
        # 10 recursos por RG
        for res_num in range(1, 11):
            res_id = f"{rg_id}/providers/Microsoft.Compute/virtualMachines/vm-{rg_num:03d}-{res_num:02d}"
            resources.append({
                "id": res_id,
                "name": f"vm-{rg_num:03d}-{res_num:02d}",
                "type": "Microsoft.Compute/virtualMachines",
                "resource_group": f"rg-{rg_num:03d}",
                "subscription_id": "sub-001",
                "location": "eastus"
            })
    
    print(f"Generando diagrama con {len(resources)} recursos...")
    
    # Medir tiempo de generación
    start_time = time.time()
    xml = generate_drawio_file(resources, dependencies, diagram_mode='infrastructure')
    end_time = time.time()
    
    generation_time = end_time - start_time
    print(f"Tiempo de generación: {generation_time:.2f}s")
    print(f"Recursos por segundo: {len(resources)/generation_time:.1f}")
    
    # Verificar que el XML es válido
    try:
        ET.fromstring(xml)
        print("✅ XML válido generado")
    except ET.ParseError as e:
        print(f"❌ Error en XML: {e}")
        return False
    
    # Guardar archivo
    with open('test-large-scale.drawio', 'w', encoding='utf-8') as f:
        f.write(xml)
    
    # Verificaciones de rendimiento
    assert generation_time < 30, f"Generación demasiado lenta: {generation_time}s"
    assert len(xml) > 100000, "XML parece incompleto"
    
    print("✅ Test de escalabilidad pasó")
    return True

if __name__ == "__main__":
    test_large_scale_performance()
```

## Ejemplo 5: Funciones Utility Comunes

```python
def is_management_group(resource_id):
    """Identifica si un recurso es un Management Group"""
    return "/managementgroups/" in resource_id.lower()

def is_subscription(resource_id):
    """Identifica si un recurso es una Subscription"""
    return resource_id.startswith("/subscriptions/") and resource_id.count("/") == 2

def is_resource_group(resource_id):
    """Identifica si un recurso es un Resource Group"""
    return "/resourcegroups/" in resource_id.lower() and resource_id.count("/") == 4

def get_resource_hierarchy_level(resource_id):
    """Retorna el nivel jerárquico del recurso (0=MG, 1=Sub, 2=RG, 3=Resource)"""
    if is_management_group(resource_id):
        return 0
    elif is_subscription(resource_id):
        return 1
    elif is_resource_group(resource_id):
        return 2
    else:
        return 3

def calculate_arc_positions(center_x, center_y, radius, num_items, downward=True):
    """Calcula posiciones en arco"""
    import math
    
    positions = []
    
    if downward:
        start_angle = math.pi  # 180°
        end_angle = 0         # 0°
    else:
        start_angle = 0       # 0°
        end_angle = math.pi   # 180°
    
    if num_items == 1:
        angle = math.pi / 2  # 90° (directamente abajo)
        positions.append((
            center_x + radius * math.cos(angle),
            center_y + radius * math.sin(angle)
        ))
    else:
        angle_step = (start_angle - end_angle) / (num_items - 1)
        for i in range(num_items):
            angle = start_angle - (i * angle_step)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions.append((x, y))
    
    return positions

def check_overlap(pos1, pos2, min_distance=150):
    """Verifica si dos posiciones se solapan"""
    import math
    
    x1, y1 = pos1
    x2, y2 = pos2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    return distance < min_distance

def adjust_positions_to_avoid_overlap(positions, min_distance=150):
    """Ajusta posiciones para evitar solapamiento"""
    adjusted = positions.copy()
    
    for i in range(len(adjusted)):
        for j in range(i + 1, len(adjusted)):
            if check_overlap(adjusted[i], adjusted[j], min_distance):
                # Separar horizontalmente
                x1, y1 = adjusted[i]
                x2, y2 = adjusted[j]
                
                if x1 == x2:  # Misma posición X
                    adjusted[i] = (x1 - min_distance/2, y1)
                    adjusted[j] = (x2 + min_distance/2, y2)
    
    return adjusted
```

Estos ejemplos proporcionan una base sólida para que GitHub Copilot entienda cómo trabajar con el proyecto y pueda generar código coherente con la arquitectura existente.

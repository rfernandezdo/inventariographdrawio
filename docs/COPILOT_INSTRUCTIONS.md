# Instrucciones para GitHub Copilot - Azure Infrastructure Diagrams

## Resumen del Proyecto

Este proyecto genera diagramas Draw.io de infraestructura Azure usando una estructura jerárquica de árbol basada en dependencias estructurales (Management Groups → Subscriptions → Resource Groups → Resources).

## Arquitectura y Estructura

### Estructura de Archivos
```
src/
├── azure_api.py         # API calls a Azure Resource Graph
├── cli.py              # Interfaz de línea de comandos
├── drawio_export.py    # Lógica principal de layout y exportación
└── utils.py            # Utilidades y funciones helper

tests/
├── unit/               # Tests unitarios
├── integration/        # Tests de integración
├── layout/            # Tests específicos de layout
├── hierarchy/         # Tests de jerarquía y escalabilidad
└── fixtures/          # Archivos .drawio de prueba
```

### Función Principal
- **`generate_drawio_file(items, dependencies, embed_data=True, include_ids=None, diagram_mode='infrastructure')`**
  - `items`: Lista de recursos Azure
  - `dependencies`: Lista de dependencias entre recursos
  - `diagram_mode`: 'infrastructure', 'components', o 'network'

## Layouts Implementados

### 1. Layout de Infraestructura (Jerárquico)
- **Algoritmo**: DFS (Depth-First Search) para construir árbol jerárquico
- **Estructura**: MG → Subscription → RG → Resources
- **Conexiones Huérfanas**: Se conectan automáticamente usando la estructura lógica de Azure

### 2. Layouts para Resource Groups
Dependiendo del número de recursos en un RG:

#### Layout Lineal (1-3 recursos)
- Recursos en línea horizontal
- Espaciado uniforme: 200px entre recursos

#### Layout en Arco (≥4 recursos)
- **Forma**: Semicírculo hacia abajo (RG arriba, recursos abajo)
- **Radio**: Calculado dinámicamente según número de recursos
- **Espaciado**: Mínimo 150px entre recursos para evitar solapamiento
- **Distribución**: Angular uniforme en el arco

## Estilos de Aristas

### Aristas Jerárquicas (Azul Sólido)
- **Estilo**: `edgeStyle=straight` (solo para RG → Resource)
- **Color**: `#1976d2` (azul)
- **Grosor**: `strokeWidth=2`
- **Uso**: Conexiones estructurales del árbol

### Aristas Ortogonales (Azul Sólido)
- **Estilo**: `edgeStyle=orthogonalEdgeStyle`
- **Color**: `#1976d2` (azul)
- **Uso**: Conexiones entre niveles superiores (MG→Subscription, Subscription→RG, MG→MG)

### Aristas de Dependencia (Gris Punteado)
- **Estilo**: `edgeStyle=orthogonalEdgeStyle;dashed=1`
- **Color**: `#666666` (gris)
- **Uso**: Dependencias no jerárquicas

## Reglas de Implementación

### 1. Identificación de Tipos de Recurso
```python
def is_management_group(resource_id):
    return "/managementgroups/" in resource_id.lower()

def is_subscription(resource_id):
    return resource_id.startswith("/subscriptions/") and resource_id.count("/") == 2

def is_resource_group(resource_id):
    return "/resourcegroups/" in resource_id.lower() and resource_id.count("/") == 4
```

### 2. Conexiones Jerárquicas vs Dependencias
- **Jerárquicas**: Solo estructura Azure (MG→Sub→RG→Resource)
- **Dependencias**: Cualquier otra relación (VM→Storage, etc.)

### 3. Layout de Arco - Parámetros Críticos
```python
# Espaciado mínimo entre recursos
min_spacing = 150

# Radio dinámico basado en número de recursos
radius = max(200, num_resources * 40)

# Arco hacia abajo (180° a 0°)
start_angle = math.pi  # 180°
end_angle = 0         # 0°
```

### 4. Generación de Aristas RG → Resource
```python
# Solo para conexiones RG → Resource usar líneas rectas
if (is_resource_group(src_id) and not is_resource_group(tgt_id) and 
    src_item.get('subscription_id') == tgt_item.get('subscription_id')):
    edge_style = "edgeStyle=straight;rounded=0;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
else:
    edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;strokeColor=#1976d2;strokeWidth=2;"
```

## Mejores Prácticas

### 1. Testing
- Siempre añadir tests para nuevas funcionalidades de layout
- Verificar tanto funcionalidad como output visual
- Tests de regresión para evitar romper layouts existentes

### 2. Escalabilidad
- Layouts deben funcionar con 1-1000+ recursos
- Usar algoritmos O(n) o O(n log n) máximo
- Evitar solapamiento de nodos en todos los casos

### 3. Modularidad
- Separar lógica de layout de exportación XML
- Funciones pequeñas y enfocadas
- Reutilizar código entre diferentes tipos de layout

### 4. Configuración
- Parámetros de espaciado como constantes configurables
- Colores y estilos centralizados
- Fácil extensión para nuevos tipos de layout

## Comandos de Desarrollo

### Ejecutar Tests
```bash
# Tests específicos de layout
python3 tests/layout/test_grid_layout.py
python3 tests/layout/test_radial_layout.py
python3 tests/layout/test_straight_edges_arc_simple.py

# Tests de integración
python3 tests/integration/test_modes.py

# Tests de jerarquía/escalabilidad
python3 tests/hierarchy/test_hierarchy.py
python3 tests/hierarchy/test_complex_tree.py
```

### Generar Diagrama
```bash
# Usando CLI
python3 src/cli.py --mode infrastructure

# Programáticamente
from drawio_export import generate_drawio_file
xml = generate_drawio_file(resources, dependencies, diagram_mode='infrastructure')
```

## Consideraciones de Rendimiento

- **Algoritmo de Layout**: O(n) para posicionamiento básico
- **Detección de Solapamiento**: O(n²) pero optimizado para casos comunes
- **Memoria**: Escalable hasta 10,000+ recursos
- **Tiempo de Generación**: ~1-5 segundos para diagramas típicos

## Extensibilidad

Para añadir nuevos tipos de layout:

1. Implementar función `generate_[tipo]_layout()`
2. Añadir lógica de selección en `generate_infrastructure_layout()`
3. Crear tests específicos en `tests/layout/`
4. Documentar parámetros y comportamiento
5. Verificar compatibilidad con estilos de aristas existentes

## Notas Importantes

- **Arco siempre hacia abajo**: RG arriba, recursos en semicírculo abajo
- **Líneas rectas solo para RG→Resource**: Otros niveles usan orthogonal
- **Espaciado adaptativo**: Se ajusta automáticamente para evitar solapamiento
- **Compatibilidad Draw.io**: XML válido para importación directa

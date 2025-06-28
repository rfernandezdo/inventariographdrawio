# Microsoft Azure dynamic diagrams with draw.io and Azure Resource Graph

Este proyecto permite generar diagramas automáticos de topologías y recursos de Azure en draw.io, a partir de datos reales obtenidos mediante Azure Resource Graph.

## Objetivo
- Automatizar la creación de diagramas de arquitectura Azure en draw.io, exportando los recursos a CSV y usando la función de importación de draw.io.
- Facilitar la visualización y documentación de entornos Azure de forma dinámica y actualizable.

## 🚀 Características Principales

### 🌳 Algoritmo DFS Jerárquico Avanzado
- **Árbol verdadero**: Implementación DFS que crea una estructura de árbol real (no solo niveles)
- **Filtrado inteligente**: Separa dependencias estructurales de Azure vs relaciones de conectividad
- **Escalabilidad probada**: Maneja >1000 recursos en <2 segundos (1,018 items/segundo)
- **25+ tipos de recursos**: Soporta todos los recursos comunes de Azure (VMs, AKS, SQL, IoT, AI/ML, etc.)

### 📊 Visualización Avanzada  
- **Líneas diferenciadas**:
  - 🔵 **Sólidas azules**: Dependencias jerárquicas (Management Group → Subscription → Resource Group → Resource)
  - ⚪ **Punteadas grises**: Relaciones de dependencia (networking, storage, etc.)
- **Iconos oficiales de Azure**: Representación visual estándar
- **Layout automático**: Centrado inteligente y disposición balanceada

### ⚡ Rendimiento Enterprise
- **Casos edge manejados**: 5 niveles de Management Groups anidados
- **Recursos especializados**: IoT Hub, Digital Twins, Synapse, Databricks, etc.
- **Conexión automática**: Elementos huérfanos se conectan por estructura lógica de Azure
- **Sin loops infinitos**: Detección de ciclos y prevención de recursión infinita

## 📁 Estructura del Proyecto (Organizada)

```
inventariographdrawio/
├── 📄 README.md              # Este archivo
├── 📄 LICENSE                # Licencia del proyecto
├── 📄 .gitignore            # Archivos ignorados por Git
│
├── 📂 src/                   # Código fuente principal
│   ├── azure_api.py         # Interacción con Azure Resource Graph
│   ├── drawio_export.py     # Generación de diagramas Draw.io (layout arco)
│   ├── cli.py               # Interfaz de línea de comandos
│   └── utils.py             # Utilidades comunes
│
├── 📂 data/                  # Datos de entrada y cache
│   ├── azure_full_hierarchy_with_icons.drawio
│   ├── masked_realistic_inventory.json
│   └── README.md
│
├── 📂 docs/                  # Documentación técnica
│   ├── CACHE_LOCAL.md       # Sistema de cache local
│   ├── DATOS_REALES.md      # Trabajo con datos reales
│   ├── DIAGRAM_MODES.md     # Modos de diagrama
│   ├── ARC_LAYOUT_FIX.md    # Layout en arco sin overlaps
│   ├── COPILOT_INSTRUCTIONS.md    # 🤖 Instrucciones para GitHub Copilot
│   ├── COPILOT_CODE_EXAMPLES.md   # 🤖 Ejemplos de código para Copilot
│   └── README.md
│
├── 📂 examples/             # Ejemplos de uso
│   ├── azure_to_drawio.py   # Ejemplo principal
│   ├── demo_cache_workflow.py
│   └── README.md
│
└── 📂 tests/                # Tests organizados (LIMPIO)
    ├── 📄 README.md         # Documentación de tests
    ├── 📄 RESULTADOS_ESCALABILIDAD.md
    │
    ├── 🎨 layout/           # Tests de layout
    │   ├── test_arc_no_overlap.py      # ⭐ TEST PRINCIPAL
    │   ├── test_grid_layout.py
    │   ├── test_radial_layout.py
    │   └── test_comparison_layouts.py
    │
    ├── 🔗 integration/      # Tests de integración
    │   ├── test_network_complete.py
    │   ├── test_network_improved.py
    │   └── test_modes.py
    │
    ├── 🧪 unit/             # Tests unitarios
    │   ├── test_cache_system.py
    │   └── test_simple.py
    │
    ├── 🏗️ Hierarchy Tests   # Tests principales (raíz)
    │   ├── test_hierarchy.py           # ⭐ TEST BÁSICO
    │   ├── test_complex_tree.py        # ⭐ TEST COMPLEJO
    │   └── test_extensive_tree.py      # Test escalabilidad
    │
    └── 📋 fixtures/         # Archivos .drawio de prueba
        ├── test-arc-layout.drawio
        ├── test-hierarchy.drawio
        └── ... (diagramas generados)
```

## 🎯 Tests Principales Recomendados

1. **`tests/layout/test_arc_no_overlap.py`** - ⭐ Verificar layout en arco sin overlaps  
2. **`tests/test_hierarchy.py`** - ⭐ Funcionalidad básica de jerarquías
3. **`tests/test_complex_tree.py`** - ⭐ Estructuras complejas
4. **`tests/layout/test_comparison_layouts.py`** - Comparar diferentes layouts

## Requisitos
- Python 3.x
- Azure CLI (`az`) y extensión `az graph`
- Permisos de lectura en la suscripción de Azure

## Instalación
```bash
# Instalar dependencias si es necesario
pip install requests

# Asegurarse de tener Azure CLI y la extensión graph
az extension add --name resource-graph
```

## Uso Básico
```bash
# Generar diagrama con todos los recursos
python src/cli.py

# Generar en modo específico
python src/cli.py --diagram-mode network

# Exportar datos a JSON
python src/cli.py --export-json inventario.json

# Usar datos offline
python src/cli.py --input-json inventario.json --output diagrama_offline.drawio
```

## 📋 Modos de Diagrama

### 🌳 `infrastructure` (Por defecto - **RECOMENDADO**)
- **Jerarquía real con DFS**: Estructura de árbol verdadera usando búsqueda en profundidad
- **Filtrado estructural**: Solo dependencias jerárquicas de Azure para el árbol principal
- **Escalabilidad probada**: >1000 recursos en <2 segundos  
- **Visualización dual**: Líneas sólidas (jerarquía) + punteadas (relaciones)
- **25+ tipos de recursos**: IoT, AI/ML, Networking avanzado, Analytics, etc.

### 📦 `components`  
- **Vista de componentes**: Agrupa recursos por función/tipo
- **Categorías funcionales**: Compute, Storage, Network, Database, Security, AI/ML, etc.

### 🌐 `network`
- **Vista de red**: Enfocada en recursos de conectividad
- **Topología de red**: VNets, Subnets, Gateways, Firewalls

## Opciones Avanzadas
- `--no-embed-data`: No incrusta todos los datos en los nodos
- `--include-ids <id1> <id2>`: Solo incluye elementos específicos y sus descendientes
- `--exclude-ids <id1> <id2>`: Excluye elementos específicos
- `--clear-cache`: Limpia la cache local
- `--use-cache`: Fuerza el uso de cache (no consulta Azure)
## Visualización en draw.io
1. Abre el archivo generado en [draw.io](https://app.diagrams.net/)
2. Selecciona todo (Ctrl+A) y usa el menú `Organizar > Disposición > Gráfico Jerárquico` para organizar el diagrama.
3. Selecciona cualquier icono y presiona Ctrl+M (Cmd+M en Mac) para ver todos sus datos incrustados.

## Navegación por el diagrama
Seguir las instrucciones de [Step through your diagram using the explore function](https://www.drawio.com/doc/faq/explore-plugin)

## Tests y Ejemplos
```bash
# Ejecutar tests
python tests/test_simple.py
python tests/test_cache_system.py

# Ejecutar ejemplos
python examples/demo_cache_workflow.py
```

## Documentación

### Para Usuarios
Ver el directorio `docs/` para documentación detallada sobre:
- Sistema de cache local
- Modos de diagrama
- Manejo de datos

### Para Desarrolladores 🤖
- **`docs/COPILOT_INSTRUCTIONS.md`**: Instrucciones completas para GitHub Copilot
- **`docs/COPILOT_CODE_EXAMPLES.md`**: Ejemplos de código y patrones de implementación
- **`tests/README.md`**: Guía completa de testing

#### Características Técnicas Implementadas
- ✅ **Layout de Arco**: Resource Groups con ≥4 recursos usan layout semicircular hacia abajo
- ✅ **Aristas Rectas**: Conexiones RG→Resource usan líneas rectas (`edgeStyle=straight`)
- ✅ **Aristas Ortogonales**: Conexiones entre niveles superiores usan líneas ortogonales
- ✅ **Sin Solapamiento**: Espaciado automático adaptativo (mínimo 150px)
- ✅ **Escalabilidad**: Probado hasta 1000+ recursos
- ✅ **Tests Organizados**: Suite completa de tests unitarios, integración y layout

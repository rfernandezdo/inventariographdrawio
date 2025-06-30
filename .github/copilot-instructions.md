# Copilot Instructions - Azure Infrastructure Diagram Generator

## Descripción del Proyecto

Este proyecto genera diagramas de infraestructura de Azure para draw.io a partir de datos reales obtenidos mediante Azure CLI y Azure Graph API. El sistema crea visualizaciones jerárquicas que muestran Management Groups, Subscriptions, Resource Groups y todos los recursos contenidos, con sus dependencias y relaciones de red.

## Arquitectura del Sistema

### Componentes Principales

1. **`src/cli.py`** - Interfaz de línea de comandos principal
2. **`src/azure_api.py`** - Extracción de datos de Azure mediante CLI y Graph API
3. **`src/drawio_export.py`** - Generación de XML de draw.io y gestión de layouts
4. **`src/utils.py`** - Utilidades auxiliares
5. **`.azure_cache/`** - Sistema de caché local para optimizar rendimiento

### Modos de Diagrama

El sistema soporta tres modos de visualización:

#### 1. Infrastructure Mode (Por defecto)
- **Propósito**: Vista jerárquica completa desde Management Groups hasta recursos individuales
- **Layout**: Árbol DFS (Depth-First Search) con layout en arco para Resource Groups con muchos recursos
- **Características**:
  - Muestra toda la jerarquía organizacional
  - Conexiones jerárquicas explícitas (padre-hijo)
  - Layout adaptativo según número de recursos
  - Iconos oficiales de Azure para cada tipo de recurso

#### 2. Components Mode
- **Propósito**: Vista orientada a componentes y servicios
- **Layout**: Agrupación por tipo de servicio
- **Uso**: Análisis de tipos de servicios y componentes utilizados

#### 3. Network Mode
- **Propósito**: Vista centrada en arquitectura de red
- **Layout**: Organización por VNets, subnets y categorías de red
- **Características especiales**:
  - Contención jerárquica: RG → VNet → Subnet → Recursos
  - Clasificación automática por función de red (edge, connectivity, security)
  - Soporte para opción `--no-hierarchy-edges`
  - Posicionamiento inteligente de recursos en contenedores

## Funcionalidades Clave

### Sistema de Caché
- **Archivos**: `.azure_cache/management_groups_YYYYMMDD_HH.json`, `.azure_cache/final_inventory_*.json`
- **Duración**: 4 horas para management groups, 1 hora para inventarios
- **Comandos**: `--no-cache`, `--force-refresh`, `--clear-cache`

### Filtrado de Enlaces Jerárquicos
- **Opción**: `--no-hierarchy-edges`
- **Función**: Elimina enlaces jerárquicos manteniendo dependencias funcionales reales
- **Enlaces filtrados**:
  - Resource Groups ↔ cualquier recurso (dependencias de contención)
  - VNet ↔ Subnet (dependencias de infraestructura)
  - Private Endpoints ↔ VNets/Subnets (dependencias jerárquicas)
  - Network Interfaces ↔ VNets/Subnets (dependencias jerárquicas)
  - Virtual Network Links ↔ VNets (dependencias jerárquicas específicas)
- **Resultado**: De ~100 dependencias → ~21 enlaces funcionales conservados
- **Uso**: Simplificar diagramas de red enfocándose solo en dependencias funcionales

### Gestión de Dependencias
- **Extracción**: Automática desde propiedades de recursos de Azure
- **Tipos soportados**:
  - Referencias de subnet en recursos de red
  - Conexiones de VPN y ExpressRoute
  - Private endpoints y DNS zones
  - Referencias entre servicios (storage accounts, key vaults, etc.)
- **Filtrado inteligente**: Sistema avanzado para eliminar dependencias jerárquicas preservando funcionales

### Recursos "Hidden" y Estilos Especiales
- **Tipos catalogados como "hidden"**:
  - `microsoft.network/privatednszones/virtualnetworklinks`
- **Estilo visual**: Cubo azul sombreado con opacidad reducida
- **Propósito**: Identificar recursos auxiliares que normalmente no se muestran en diagramas principales
- **Configuración**: Variable `HIDDEN_RESOURCE_TYPES` en `drawio_export.py`

## Detalles Técnicos del Layout

### Network Mode - Layout Jerárquico
```
Subscription Container
├── Resource Group Container (dinámicamente dimensionado)
│   ├── VNet Container (ancho: max(600px, contenido + 120px))
│   │   ├── Subnet Container (centrado, margen mínimo 60px)
│   │   │   └── Recursos de Subnet (2 por fila, espaciado 150px)
│   │   └── Recursos Directos VNet (3 por fila, espaciado 140px)
│   └── Recursos Standalone RG (3 por fila, espaciado 120px)
└── Management Panel (lateral, 300px ancho)
```

### Cálculo de Dimensiones
- **Resource Groups**: Dinámico basado en contenido, máximo 900x1200px
- **VNets**: `max(600px, contenido + 120px)` ancho, altura calculada según subnets + recursos directos
- **Subnets**: Centrados en VNet, máximo 2 recursos por fila
- **Padding**: Muy generoso para evitar solapamientos (80-120px entre secciones)

### Identificadores y Referencias
- **Cell IDs**: `node-{index}` para recursos, `group_{tipo}_{counter}` para contenedores
- **Parent IDs**: Sistema de contención jerárquica estricta
- **Azure IDs**: Normalizados a lowercase para consistency

## Iconos y Estilos

### Sistema de Iconos
- **Fuente**: Iconos oficiales de Azure (`img/lib/azure2/`, `img/lib/mscae/`)
- **Fallbacks**: Estilos genéricos para tipos no reconocidos
- **Mapping**: Diccionario `AZURE_ICONS` en `drawio_export.py`

### Estilos de Contenedores
- **Management Groups**: Hexágono verde (`#d5e8d4`)
- **Subscriptions**: Rectángulo amarillo (`#fff2cc`)
- **Resource Groups**: Rectángulo naranja (`#fff8e1`)
- **VNets**: Rectángulo verde (`#e8f5e8`)
- **Subnets**: Rectángulo púrpura (`#f3e5f5`)

### Estilos Especiales
- **Recursos Hidden**: Cubo azul sombreado (`fillColor=#dae8fc;strokeColor=#6c8ebf;opacity=60`)
- **Containers sin labels**: RG, VNet y Subnet containers sin texto para evitar redundancia visual
- **Nombres posicionados**: Texto de containers aparece a la derecha del icono

## Comandos Principales

### Generación Básica
```bash
python src/cli.py                                    # Modo infrastructure por defecto
python src/cli.py --diagram-mode network            # Modo network
python src/cli.py --diagram-mode components         # Modo components
```

### Opciones Avanzadas
```bash
python src/cli.py --no-hierarchy-edges              # Sin enlaces jerárquicos
python src/cli.py --no-embed-data                   # Sin datos embebidos
python src/cli.py --include-ids ID1 ID2             # Solo IDs específicos
python src/cli.py --exclude-ids ID1 ID2             # Excluir IDs específicos
python src/cli.py --output archivo.drawio           # Archivo de salida personalizado
```

### Gestión de Caché
```bash
python src/cli.py --no-cache                        # Sin usar caché
python src/cli.py --force-refresh                   # Forzar actualización
python src/cli.py --clear-cache                     # Limpiar caché
```

## Solución de Problemas

### Layout y Contención
- **Problema**: Recursos fuera de contenedores
- **Causa**: Cálculo insuficiente de dimensiones de contenedores
- **Solución**: Ajustar padding y dimensiones máximas en `generate_network_layout()`

### Performance
- **Problema**: Consultas lentas a Azure
- **Solución**: Usar sistema de caché, ajustar timeouts en `azure_api.py`

### Dependencias Faltantes
- **Problema**: Enlaces no aparecen
- **Causa**: Filtros de dependencias demasiado estrictos
- **Solución**: Revisar lógica de filtrado en `filter_dependencies_for_no_hierarchy_edges()`

### Filtrado de Dependencias
- **Problema**: Dependencias jerárquicas aparecen con `--no-hierarchy-edges`
- **Causa**: Lógica de filtrado insuficiente para ciertos tipos de recursos
- **Solución**: Ajustar patrones en `HIERARCHICAL_NETWORK_TYPES` y condiciones de filtrado

## Patrones de Código

### Estructura de Recursos
```python
item = {
    'id': 'azure_resource_id',
    'name': 'resource_name',
    'type': 'microsoft.service/resourcetype',
    'location': 'region',
    'properties': {...},
    'subnet_id': 'subnet_reference',  # Si aplica
    'parent_vnet_id': 'vnet_reference'  # Si aplica
}
```

### Creación de Contenedores
```python
group_info.append({
    'id': 'unique_group_id',
    'parent_id': 'parent_container_id',
    'type': 'container_type',
    'x': x_position,
    'y': y_position,
    'width': calculated_width,
    'height': calculated_height,
    'label': 'Display Label',
    'style': 'draw.io_style_string'
})
```

### Posicionamiento de Recursos
```python
node_positions[resource_index] = (x_coordinate, y_coordinate)
resource_to_parent_id[resource_index] = 'parent_container_id'
```

## Testing y Validación

### Herramientas de Análisis
- **`check_icon_coverage.py`** - Verifica cobertura de iconos en el diccionario `AZURE_ICONS`
- **`compare_dependencies.py`** - Compara dependencias entre modo normal y `--no-hierarchy-edges`

### Archivos de Test Importantes
- **`tests/integration/test_network_real_data.py`** - Tests con datos reales
- **`tests/layout/test_*.py`** - Tests específicos de layout
- **`tests/fixtures/*.drawio`** - Casos de prueba de referencia

### Validación Manual
1. Generar diagrama: `python src/cli.py --diagram-mode network --output test.drawio`
2. Abrir en draw.io y verificar:
   - Recursos dentro de contenedores correctos
   - Sin solapamientos visuales
   - Enlaces apropiados según modo
   - Iconos correctos para cada tipo de recurso
   - Recursos "hidden" con estilo especial (cubo azul sombreado)
   - Con `--no-hierarchy-edges`: Solo ~21 enlaces funcionales (no jerárquicos)

### Validación de Dependencias
1. Comparar modos: `python compare_dependencies.py`
2. Verificar filtrado: Enlaces eliminados vs conservados
3. Confirmar que dependencias VNet/Subnet se filtran correctamente
4. Validar que dependencias funcionales importantes se mantienen

## Extensibilidad

### Añadir Nuevos Tipos de Recursos
1. Actualizar `AZURE_ICONS` en `drawio_export.py`
2. Agregar lógica de clasificación en `generate_network_layout()` si es necesario
3. Actualizar tests correspondientes

### Nuevos Modos de Diagrama
1. Crear función `generate_{mode}_layout()` en `drawio_export.py`
2. Actualizar `generate_drawio_file()` para incluir el nuevo modo
3. Añadir opción en `cli.py`

### Optimizaciones de Performance
- Implementar consultas paralelas en `azure_api.py`
- Mejorar algoritmos de layout para datasets grandes
- Optimizar sistema de caché con compresión

---

**Nota**: Este proyecto maneja datos sensibles de infraestructura. Siempre usar archivos enmascarados para tests y documentación pública.
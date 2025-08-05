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

El sistema soporta cuatro modos de visualización:

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
  - **Soporte Multi-Subnet para NSGs y Route Tables**:
    - NSGs asociados a múltiples subnets aparecen como elemento original en RG + copias "(asignación)" en cada subnet
    - Route Tables asociados a múltiples subnets aparecen como elemento original en RG + copias "(asignación)" en cada subnet
    - IDs únicos para elementos virtuales (`--assignment-N`) para evitar conflictos en draw.io
    - Metadatos incluidos: `_virtual_subnet_id`, `_original_index`, `_is_assignment`

#### 4. All Mode (Multipágina)
- **Propósito**: Todas las vistas en un solo archivo draw.io con páginas separadas
- **Layout**: Combina todos los modos anteriores
- **Características especiales**:
  - 4 páginas separadas en un solo archivo:
    - Página 1: Infrastructure (jerarquía completa)
    - Página 2: Components (agrupado por función)
    - Página 3: Network (recursos de red con enlaces jerárquicos)
    - Página 4: Network (Clean) (recursos de red sin enlaces jerárquicos)
  - Navegación mediante pestañas en draw.io
  - Vista integral de toda la infraestructura Azure
  - Filtrado automático de dependencias en página Network (Clean)

## Funcionalidades Clave

### Soporte Multi-Subnet para NSGs y Route Tables
- **Problema resuelto**: NSGs y Route Tables pueden estar asociados a múltiples subnets simultáneamente
- **Implementación**:
  - **Elemento Original**: Permanece en su Resource Group de origen
  - **Elementos de Asignación**: Copias virtuales "(asignación)" en cada subnet asociada
  - **Detección automática**: Utiliza `properties.subnets[]` array de NSGs y Route Tables
  - **IDs únicos**: Elementos virtuales usan sufijo `--assignment-N` para evitar conflictos
- **Funciones clave**:
  - `_find_all_subnets_for_nsg()`: Encuentra todas las subnets asociadas a un NSG
  - `_find_all_subnets_for_route_table()`: Encuentra todas las subnets asociadas a una Route Table
  - Sistema de elementos extendidos (`extended_items`) que incluye originales + virtuales
- **Metadatos de elementos virtuales**:
  ```python
  virtual_element = {
      'name': 'original-name (asignación)',
      'id': 'original-id--assignment-N',
      '_is_assignment': True,
      '_virtual_subnet_id': 'subnet_id',
      '_original_index': original_index
  }
  ```
- **Arquitectura visual**: Representa correctamente la arquitectura Azure donde un NSG/RT está en RG pero "asignado" a múltiples subnets

### Modo All (Multipágina)
- **Archivo único**: Todas las vistas en un solo archivo draw.io
- **4 páginas separadas**:
  1. **Infrastructure**: Jerarquía completa con conexiones padre-hijo
  2. **Components**: Agrupación por tipo de servicio y función
  3. **Network**: Vista de red con enlaces jerárquicos completos
  4. **Network (Clean)**: Vista de red solo con dependencias funcionales (~21 enlaces vs ~100)
- **Navegación**: Pestañas en draw.io para cambiar entre vistas
- **Compatibilidad**: Funciona con todas las opciones de filtrado y configuración
- **Uso**: `--diagram-mode all`

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
│   ├── NSG Original (cuando está asociado a múltiples subnets)
│   ├── Route Table Original (cuando está asociado a múltiples subnets)
│   ├── VNet Container (ancho: max(600px, contenido + 120px))
│   │   ├── Subnet Container (centrado, margen mínimo 60px)
│   │   │   ├── NSG (asignación) - solo si está asociado a esta subnet
│   │   │   ├── Route Table (asignación) - solo si está asociado a esta subnet
│   │   │   └── Recursos de Subnet (2 por fila, espaciado 150px)
│   │   └── Recursos Directos VNet (3 por fila, espaciado 140px)
│   └── Recursos Standalone RG (3 por fila, espaciado 120px)
└── Management Panel (lateral, 300px ancho)
```

### Gestión de Elementos Extendidos
- **Array original (`items`)**: Recursos obtenidos de Azure API
- **Array extendido (`extended_items`)**: Incluye elementos originales + virtuales de asignación
- **Mapeo de posiciones**: `node_positions` usa índices de `extended_items`
- **Contención**: `resource_to_parent_id` mapea elementos virtuales a sus contenedores apropiados
- **Wrapper compatibility**: `generate_network_layout_wrapper()` maneja compatibilidad entre sistemas legacy y modular

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
python src/cli.py --diagram-mode all               # Modo all (multipágina)
```

### Opciones Avanzadas
```bash
python src/cli.py --diagram-mode all               # Todas las vistas en páginas separadas
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

### Función de Layout de Red con Soporte Multi-Subnet
```python
def generate_network_layout(items, dependencies):
    """
    Genera layout de red con soporte para NSGs y Route Tables multi-subnet
    
    Returns:
        tuple: (extended_items, node_positions, group_info, resource_to_parent_id)
        - extended_items: Array que incluye elementos originales + virtuales
        - node_positions: Posiciones de todos los elementos (índices de extended_items)
        - group_info: Información de contenedores jerárquicos
        - resource_to_parent_id: Mapeo elemento → contenedor padre
    """
    
    # Detectar NSGs/RTs multi-subnet y crear elementos virtuales
    for i, item in enumerate(items):
        if item['type'].lower() == 'microsoft.network/networksecuritygroups':
            subnets = _find_all_subnets_for_nsg(item, items)
            for j, subnet_id in enumerate(subnets):
                virtual_element = create_virtual_assignment(item, subnet_id, i, j)
                extended_items.append(virtual_element)
```

### Detección de Subnets Asociadas
```python
def _find_all_subnets_for_nsg(nsg_item, all_items):
    """
    Encuentra todas las subnets asociadas a un NSG
    
    Args:
        nsg_item: Elemento NSG con properties.subnets array
        all_items: Lista completa de elementos para normalización de IDs
    
    Returns:
        list: IDs normalizados de subnets asociadas
    """
    subnets = nsg_item.get('properties', {}).get('subnets', [])
    return [normalize_subnet_id(subnet['id'], all_items) for subnet in subnets]
```

### Creación de Elementos Virtuales
```python
def create_virtual_assignment_element(original_item, subnet_id, original_index, assignment_index):
    """
    Crea elemento virtual de asignación para multi-subnet
    
    Returns:
        dict: Elemento virtual con metadatos especiales
    """
    virtual_element = original_item.copy()
    virtual_element['name'] = f"{original_item['name']} (asignación)"
    virtual_element['id'] = f"{original_item['id']}--assignment-{assignment_index}"
    virtual_element['_is_assignment'] = True
    virtual_element['_virtual_subnet_id'] = subnet_id
    virtual_element['_original_index'] = original_index
    return virtual_element
```

### Función Multipágina
```python
def generate_drawio_multipage_file(items, dependencies, embed_data=True, include_ids=None, no_hierarchy_edges=False):
    """
    Genera archivo draw.io con múltiples páginas (Infrastructure, Components, Network, Network Clean)
    
    Args:
        items: Lista de recursos de Azure
        dependencies: Lista de dependencias entre recursos  
        embed_data: Si incrustar datos completos o solo el tipo
        include_ids: IDs específicos a incluir
        no_hierarchy_edges: Si aplicar filtrado para página Network (Clean)
    
    Returns:
        str: Contenido XML del archivo draw.io con múltiples páginas
    """
```

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

### Archivos de Demostración Multi-Subnet
- **`examples/demo_multi_subnet_generator.py`** - Generador de datos de demostración con NSGs y Route Tables multi-subnet
- **`data/demo_multi_subnet_example.json`** - Datos de ejemplo con configuración multi-subnet realista
- **`data/test_multi_subnet.json`** - Datos de prueba simples para validación básica

### Casos de Prueba Multi-Subnet
```bash
# Test básico con datos de ejemplo
python src/cli.py --input-json data/test_multi_subnet.json --diagram-mode network --all-tenants

# Test con datos de demostración compleja
python examples/demo_multi_subnet_generator.py
python src/cli.py --input-json data/demo_multi_subnet_example.json --diagram-mode network --all-tenants
```

### Validación Manual
1. Generar diagrama: `python src/cli.py --diagram-mode network --output test.drawio`
2. Abrir en draw.io y verificar:
   - Recursos dentro de contenedores correctos
   - Sin solapamientos visuales
   - Enlaces apropiados según modo
   - Iconos correctos para cada tipo de recurso
   - Recursos "hidden" con estilo especial (cubo azul sombreado)
   - Con `--no-hierarchy-edges`: Solo ~21 enlaces funcionales (no jerárquicos)
   - **Verificación Multi-Subnet**:
     - NSGs originales en Resource Groups (sin sufijo "(asignación)")
     - NSGs "(asignación)" dentro de subnets correspondientes
     - Route Tables originales en Resource Groups
     - Route Tables "(asignación)" dentro de subnets correspondientes
     - IDs únicos para elementos virtuales (sufijo `--assignment-N`)
     - Metadatos `_is_assignment`, `_virtual_subnet_id`, `_original_index` en elementos virtuales

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

### Extender Soporte Multi-Subnet a Otros Recursos
1. **Identificar tipo de recurso**: Determinar qué recursos Azure soportan asociaciones múltiples
2. **Crear función de detección**: Similar a `_find_all_subnets_for_nsg()` pero adaptada al recurso
3. **Añadir lógica en layout**: Incluir en el bucle de generación de elementos virtuales
4. **Ejemplo para Application Security Groups**:
   ```python
   def _find_all_subnets_for_asg(asg_item, all_items):
       # Lógica específica para ASGs
       pass
   
   # En generate_network_layout():
   elif item_type == 'microsoft.network/applicationsecuritygroups':
       subnets = _find_all_subnets_for_asg(item, items)
       # Crear elementos virtuales
   ```

### Nuevos Modos de Diagrama
1. Crear función `generate_{mode}_layout()` en `drawio_export.py`
2. Actualizar `generate_drawio_file()` para incluir el nuevo modo
3. Añadir opción en `cli.py`
4. Para modos multipágina, usar `generate_drawio_multipage_file()` como referencia

### Optimizaciones de Performance
- Implementar consultas paralelas en `azure_api.py`
- Mejorar algoritmos de layout para datasets grandes
- Optimizar sistema de caché con compresión

## Consideraciones de Seguridad y Datos Sensibles

### Políticas de Datos
- **Principio**: Nunca exponer datos reales de infraestructura en documentación pública o archivos trackeados por git
- **Archivos permitidos con datos reales**: Solo en [`.azure_cache/`](.azure_cache/) (incluido en [`.gitignore`](.gitignore))
- **Archivos públicos**: Deben usar solo datos ficticios claramente identificables

### Datos que Deben Enmascararse
- **Tenant IDs**: Usar valores ficticios como `aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee`
- **Subscription IDs**: Usar prefijos como `demo-subscription-001`
- **Nombres organizacionales**: Usar nombres genéricos como "Corporativo Demo"
- **IPs y rangos de red**: Usar rangos RFC 1918 estándar (10.0.0.0/16, etc.)
- **Nombres de recursos**: Usar prefijos como `demo-`, `test-`, `example-`

### Archivos a Verificar Regularmente
- `README.md` - Ejemplos en documentación
- `docs/*.md` - Toda la documentación
- `src/cli.py` - Mensajes de ayuda y ejemplos
- `examples/*.py` - Scripts de demostración
- `data/*.json` - Archivos de datos de ejemplo (NO caché)

### Procedimiento de Limpieza
1. Buscar tenant IDs reales: `grep -r "df1b7014\|[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}" . --exclude-dir=.azure_cache`
2. Buscar nombres organizacionales: `grep -r -i "organization\|company\|corp" . --exclude-dir=.azure_cache`
3. Reemplazar con valores ficticios usando patrones consistentes

---

**CRÍTICO**: Este proyecto maneja datos sensibles de infraestructura. Siempre usar archivos enmascarados para tests y documentación pública. Verificar regularmente que no se filtren datos reales en archivos trackeados por git.
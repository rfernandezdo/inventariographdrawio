# Azure Infrastructure Diagrams for Draw.io

[![GitHub Action](https://img.shields.io/badge/GitHub-Action-blue?logo=github-actions&logoColor=white)](https://github.com/marketplace/actions/azure-infrastructure-diagrams-for-draw-io)
[![Version](https://img.shields.io/github/v/release/rfernandezdo/inventariographdrawio?include_prereleases&label=version)](https://github.com/rfernandezdo/inventariographdrawio/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](https://www.python.org)
[![Azure](https://img.shields.io/badge/Azure-Resource%20Graph-0078d4.svg?logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/en-us/services/azure-resource-graph/)

Generador automático de diagramas de infraestructura Azure dinámicos para draw.io, utilizando datos reales obtenidos mediante Azure Resource Graph API. **Disponible como GitHub Action y herramienta CLI.**

## 🚀 Uso Rápido

### ⚠️ Migración a v2.0
Si estás actualizando desde v1.x, consulta la [guía de migración](MIGRATION_GUIDE_V2.md) para migrar a la nueva autenticación OIDC.

### 🤖 Como GitHub Action (Recomendado)
```yaml
- name: Azure Login
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

- name: Generate Azure Infrastructure Diagram
  uses: rfernandezdo/inventariographdrawio@v1
  with:
    diagram-mode: 'all'
    output-path: 'docs/azure-infrastructure.drawio'
    commit-changes: 'pr'
```
[📖 **Configuración completa en 5 minutos**](SETUP_GITHUB_ACTION.md) | [📋 **15+ ejemplos de workflows**](EXAMPLES.md)

### 👨‍💻 Como CLI Local
```bash
python src/cli.py --diagram-mode all --output mi-infraestructura.drawio
```

## Objetivos
- 🤖 **Automatización completa**: GitHub Action para integración CI/CD
- 📊 **Visualización dinámica**: Diagramas actualizados automáticamente desde Azure Resource Graph
- 🏢 **Multi-tenant**: Soporte para entornos empresariales complejos
- ⚡ **Alto rendimiento**: Procesamiento de 1000+ recursos en segundos

## 🎯 Casos de Uso

### 🤖 Automatización con GitHub Actions
- **Informes semanales**: Diagramas automáticos cada lunes
- **Detección de cambios**: Notificaciones cuando cambia la infraestructura  
- **Documentación viva**: PRs automáticos con diagramas actualizados
- **Múltiples entornos**: Diagramas separados por tenant/suscripción

### 👨‍💻 Uso Local/Manual
- **Auditorías rápidas**: Generar diagrama completo en minutos
- **Análisis de arquitectura**: Visualizar dependencias y relaciones
- **Documentación técnica**: Exportar a draw.io para presentaciones
- **Análisis offline**: Usar JSON exports para procesamiento personalizado

Ver [ACTION_README.md](ACTION_README.md) para documentación completa de la GitHub Action.

## 🚀 Características Principales

### � Filtrado por Tenant (NUEVO)
- **Multi-tenant**: Soporte para filtrar recursos por Tenant ID específico
- **Detección automática**: Usa el tenant actual del CLI de Azure por defecto
- **Separación limpia**: Diagramas completamente separados por tenant
- **Listado de tenants**: Muestra todos los tenants disponibles con sus suscripciones

### �🌳 Algoritmo DFS Jerárquico Avanzado
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

## Instalación y Configuración

### GitHub Action (Recomendado)
1. **Crear Service Principal Azure**:
```bash
az ad sp create-for-rbac --name "GitHub-Azure-Diagrams" --role "Reader" --scopes /subscriptions/{subscription-id} --sdk-auth
```

2. **Configurar secreto en GitHub**:
   - Ve a `Settings > Secrets and variables > Actions`
   - Crea `AZURE_CREDENTIALS` con la salida del comando anterior

3. **Crear workflow**:
```yaml
name: Azure Infrastructure Diagrams
on:
  workflow_dispatch:
  schedule:
    - cron: '0 6 * * 1'  # Lunes 6 AM

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: rfernandezdo/inventariographdrawio@v1
        with:
          azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
          diagram-mode: 'all'
          commit-changes: 'pr'
```

### CLI Local
```bash
# Requisitos
pip install requests
az extension add --name resource-graph

# Uso básico
python src/cli.py
```

## Uso

### 🤖 Como GitHub Action

#### Diagrama Básico de Infraestructura
```yaml
- name: Azure Login
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

- name: Generate Infrastructure Diagram
  uses: rfernandezdo/inventariographdrawio@v1
  with:
    output-path: 'docs/infrastructure.drawio'
```

#### Diagrama Completo con Pull Request
```yaml
- name: Generate All Diagrams
  uses: rfernandezdo/inventariographdrawio@v1
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
    diagram-mode: 'all'
    export-json: 'docs/azure-inventory.json'
    commit-changes: 'pr'
    pr-title: 'Update Azure Infrastructure'
```

#### Por Tenant Específico
```yaml
- name: Generate Production Diagram
  uses: rfernandezdo/inventariographdrawio@v1
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
    tenant-filter: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    include-ids: '/subscriptions/prod-sub-id'
    commit-changes: 'push'
    target-branch: 'prod-docs'
```

### 👨‍💻 Como CLI Local

#### Básico
```bash
# Generar diagrama con todos los recursos (usa tenant actual automáticamente)
python src/cli.py

# Generar en modo específico
python src/cli.py --diagram-mode network

# Exportar datos a JSON
python src/cli.py --export-json inventario.json

# Usar datos offline
python src/cli.py --input-json inventario.json --output diagrama_offline.drawio
```

#### 🏢 Filtrado por Tenant
```bash
# Listar todos los tenants disponibles
python src/cli.py --list-tenants

# Filtrar por tenant específico
python src/cli.py --tenant-filter aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee

# Incluir todos los tenants (comportamiento anterior)
python src/cli.py --all-tenants

# Generar diagramas separados por tenant
python src/cli.py --tenant-filter TENANT_A --output tenant_a.drawio
python src/cli.py --tenant-filter TENANT_B --output tenant_b.drawio
```

**Beneficios del filtrado por tenant:**
- ✅ Diagramas limpiamente separados por organización
- ✅ Evita confusión en entornos multi-tenant
- ✅ Detección automática del tenant actual (comportamiento por defecto)
- ✅ Compatible con todos los modos de diagrama

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
- `--tenant-filter <TENANT_ID>`: Filtrar recursos por Tenant ID específico
- `--all-tenants`: Incluir recursos de todos los tenants
- `--list-tenants`: Listar todos los tenants disponibles
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

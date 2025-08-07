# Modos de Diagrama - Azure Infrastructure Diagrams

Este documento describe los diferentes modos de diagrama disponibles en Azure Infrastructure Diagrams, tanto para uso como CLI local como GitHub Action, basados en las recomendaciones de [Microsoft Learn sobre diagramas de diseño de arquitectura](https://learn.microsoft.com/es-es/azure/well-architected/architect-role/design-diagrams).

## 🎯 Modos Disponibles

### 1. Infrastructure Mode (Por Defecto - **RECOMENDADO**)

#### Como GitHub Action
```yaml
- uses: rfernandezdo/inventariographdrawio@v2
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
    diagram-mode: 'infrastructure'  # o simplemente omitir (es el defecto)
```

#### Como CLI Local
```bash
python src/cli.py --diagram-mode infrastructure
python src/cli.py  # (modo por defecto)
```

**Propósito**: Diagrama de implementación que muestra la jerarquía completa de Azure como un árbol jerárquico.

**🌳 Algoritmo de Árbol DFS Avanzado**:
- **Búsqueda en profundidad**: Crea una estructura de árbol real (no solo niveles)
- **Filtrado inteligente**: Solo usa relaciones estructurales de Azure para el árbol principal
- **Escalabilidad probada**: Maneja >1000 recursos en <2 segundos (1,018 items/segundo)
- **25+ tipos de recursos**: Soporta todos los recursos comunes de Azure

**📊 Visualización Diferenciada**:
- 🔵 **Líneas sólidas azules**: Dependencias jerárquicas (Management Group → Subscription → Resource Group → Resource)
- ⚪ **Líneas punteadas grises**: Relaciones de dependencia (networking, storage, etc.)
- � **Nodo raíz inteligente**: Crea nodo virtual "Azure Tenant" si no hay Management Groups
- 📐 **Layout perfecto**: Centrado automático y disposición balanceada

**Ejemplo de jerarquía real**:
```
🏢 Azure Tenant (Root) ← Nodo raíz virtual
├── � contoso-connectivity ← Management Group raíz  
│   ├── 📊 contoso-platform ← MG hijo
│   │   └── 📊 contoso-root ← MG nieto
│   │       └── 📋 contoso-prod-001 ← Suscripción
│   │           ├── 📁 rg-network-prd-we-001 ← Resource Group
│   │           │   ├── 🌐 vnet-hub-prd-we-001 ← VNet
│   │           │   ├── 🔗 snet-gateway-prd-we-001 ← Subnet
│   │           │   └── 🌐 pip-gateway-prd-we-001 ← Public IP
│   │           └── 📁 rg-compute-prd-we-001 ← Resource Group
│   │               └── 🛡️ nsg-compute-prd-we-001 ← NSG  
3. **Conexión**: Conecta elementos huérfanos por estructura de IDs de Azure
```
**Uso recomendado**: 
- 🤖 **GitHub Action**: Informes automáticos de infraestructura completa
- 👨‍💻 **CLI Local**: Auditorías y documentación de arquitectura

---

### 2. Components Mode

#### Como GitHub Action
```yaml
- uses: rfernandezdo/inventariographdrawio@v2
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
    diagram-mode: 'components'
```

#### Como CLI Local

</details>

### 2. Components Mode
```bash
python src/cli.py --diagram-mode components
```

**Propósito**: Diagrama de componentes que agrupa recursos por función/tipo.

**Características**:
- Agrupa recursos por categorías funcionales:
  - **Governance**: Management Groups, Suscripciones, Resource Groups
  - **Compute**: VMs, App Services, AKS, Container Instances
  - **Storage**: Storage Accounts, Disks, File Shares
  - **Network**: VNets, Load Balancers, Firewalls, Public IPs
  - **Database**: SQL Server, CosmosDB, Database for MySQL/PostgreSQL
  - **Security**: Key Vaults, Managed Identity, Security Center
  - **AI/ML**: Cognitive Services, Machine Learning Workspaces
  - **Management**: Log Analytics, Application Insights, Automation
  - **Other**: Recursos que no encajan en las categorías anteriores

- Disposición horizontal por grupos
- Útil para entender la arquitectura por capas funcionales
- Ideal para presentaciones y análisis de costos por categoría

**Equivale a**: Diagrama de componentes según Microsoft Learn

### 3. Network Mode
```bash
python src/cli.py --diagram-mode network
```

**Propósito**: Diagrama de red centrado en conectividad y recursos de networking, con estructura visual similar a los diagramas oficiales de Azure.

**Características**:
- Muestra recursos relacionados con la red y governance de forma estructurada
- **Agrupadores visuales**: VNets se muestran como contenedores grandes con subnets organizadas dentro
- **Recursos dentro de subnets**: VMs, App Services y otros recursos se posicionan automáticamente dentro de sus subnets correspondientes (como en la imagen de referencia)
- Organizado por capas de red:
  - **Governance**: Management Groups, Suscripciones, Resource Groups (arriba)
  - **Internet**: Public IPs, Traffic Manager, DNS Zones
  - **Edge**: Application Gateway, Azure Firewall
  - **Load Balancing**: Load Balancers
  - **Virtual Networks**: VNets como contenedores con subnets dentro, y recursos posicionados dentro de cada subnet
  - **Connectivity**: VPN Gateways, ExpressRoute, Connections
  - **Network Security**: NSGs, Route Tables
  - **Other**: Recursos que no se pueden asociar a una subnet específica

- **Disposición estructurada**: Cada VNet se muestra como un contenedor rectangular con líneas punteadas, y las subnets se posicionan dentro como elementos organizados
- **Zonas claramente definidas**: Similar a los diagramas oficiales de Microsoft con contenedores para availability zones y subnets
- Útil para análisis de seguridad de red, troubleshooting y diseño de conectividad
- Ideal para equipos de networking y security

**Equivale a**: Diagrama de red según Microsoft Learn, con inspiración visual de los diagramas oficiales de Azure

## Ejemplos de Uso

### Caso 1: Auditoría Completa de Infraestructura
```bash
python src/cli.py --diagram-mode infrastructure
```
Genera un diagrama completo mostrando toda la jerarquía de Azure.

### Caso 2: Análisis de Arquitectura por Componentes
```bash
python src/cli.py --diagram-mode components --include-ids /subscriptions/xxx-xxx-xxx
```
Muestra los recursos de una suscripción específica agrupados por función.

### Caso 3: Revisión de Seguridad de Red
```bash
python src/cli.py --diagram-mode network
```
Enfocado en recursos de red para análisis de conectividad y seguridad.

### Caso 4: Documentación de Entorno de Desarrollo
```bash
python src/cli.py --diagram-mode components --include-ids /subscriptions/dev-subscription-id --no-embed-data
```
Diagrama simplificado de componentes para un entorno específico.

```bash
python src/cli.py --diagram-mode components
```

**Propósito**: Agrupa recursos por función y tipo de servicio para análisis arquitectónico.

**Características**:
- 📦 **Agrupación funcional**: Compute, Storage, Network, Database, Security, AI/ML, etc.
- 🎯 **Vista de servicios**: Ideal para análisis de costos y tecnologías utilizadas
- 📊 **Resumen de arquitectura**: Visión general de componentes sin jerarquía organizacional

**Uso recomendado**:
- 🤖 **GitHub Action**: Análisis de componentes utilizados por entorno
- 👨‍💻 **CLI Local**: Presentaciones ejecutivas y análisis de servicios

---

### 3. Network Mode

#### Como GitHub Action
```yaml
- uses: rfernandezdo/inventariographdrawio@v2
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
    diagram-mode: 'network'
    no-hierarchy-edges: true  # Opcional: solo dependencias funcionales
```

#### Como CLI Local
```bash
python src/cli.py --diagram-mode network
python src/cli.py --diagram-mode network --no-hierarchy-edges  # Solo deps funcionales
```

**Propósito**: Vista centrada en recursos de red y topología de conectividad.

**🌐 Características Avanzadas**:
- **Contención jerárquica**: RG → VNet → Subnet → Recursos
- **Multi-Subnet Support**: NSGs y Route Tables aparecen tanto en RG original como asignados a subnets
- **Filtrado inteligente**: Opción `--no-hierarchy-edges` para mostrar solo ~21 dependencias funcionales vs ~100 jerárquicas
- **Clasificación automática**: Recursos categorizados por función (edge, connectivity, security)

**Elementos especiales**:
- 🔵 **NSGs multi-subnet**: Elemento original en RG + copias "(asignación)" en cada subnet
- 🔧 **Route Tables multi-subnet**: Elemento original en RG + copias "(asignación)" en cada subnet  
- 👻 **Recursos "hidden"**: Cubo azul sombreado para elementos auxiliares

**Uso recomendado**:
- 🤖 **GitHub Action**: Diagramas de topología de red para análisis de conectividad
- 👨‍💻 **CLI Local**: Análisis de arquitectura de red y troubleshooting

---

### 4. All Mode (Multi-página - **RECOMENDADO para GitHub Action**)

#### Como GitHub Action
```yaml
- uses: rfernandezdo/inventariographdrawio@v2
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
    diagram-mode: 'all'  # Un solo archivo, múltiples páginas
```

#### Como CLI Local
```bash
python src/cli.py --diagram-mode all
```

**Propósito**: Todas las vistas en un solo archivo draw.io con páginas separadas.

**📄 4 Páginas en un solo archivo**:
1. **Infrastructure**: Jerarquía completa con conexiones padre-hijo
2. **Components**: Agrupación por tipo de servicio y función  
3. **Network**: Vista de red con enlaces jerárquicos completos
4. **Network (Clean)**: Vista de red solo con dependencias funcionales (~21 enlaces vs ~100)

**Ventajas del modo All**:
- 🎯 **Un solo archivo**: Todas las vistas en un archivo consolidado
- 🔄 **Navegación fácil**: Pestañas en draw.io para cambiar entre vistas
- 📊 **Vista integral**: Análisis completo desde diferentes perspectivas
- 🤖 **Ideal para GitHub Action**: Genera documentación completa automáticamente

**Uso recomendado**:
- ✅ **GitHub Action**: Modo por defecto para informes automáticos completos
- ✅ **CLI Local**: Documentación completa para presentaciones y auditorías

## 🚀 Casos de Uso por Modo

### Infrastructure Mode
- ✅ **Auditorías de compliance**: Vista jerárquica completa para governance
- ✅ **Documentación oficial**: Estructura organizacional clara
- ✅ **Onboarding**: Mostrar estructura completa a nuevos miembros del equipo

### Components Mode  
- ✅ **Análisis de costos**: Agrupar por tipo de servicio para cost management
- ✅ **Presentaciones ejecutivas**: Vista de alto nivel sin detalles técnicos
- ✅ **Technology stack review**: Evaluar tecnologías utilizadas

### Network Mode
- ✅ **Troubleshooting de conectividad**: Análisis de topología de red
- ✅ **Planificación de seguridad**: Revisar NSGs, firewalls y zonas
- ✅ **Análisis de tráfico**: Entender flujos de red entre componentes

### All Mode
- ✅ **Informes automáticos**: GitHub Action genera documentación completa
- ✅ **Auditorías integrales**: Todas las perspectivas en un solo lugar
- ✅ **Documentación viva**: Actualizaciones automáticas con PRs

### 🎯 Características Visuales y Layout

#### Layout Jerárquico (Infrastructure Mode)
- ✅ **DFS Tree Algorithm**: Estructura de árbol real usando búsqueda en profundidad
- ✅ **Centrado automático**: Padres centrados respecto a sus hijos
- ✅ **Sin solapamientos**: Espaciado inteligente adaptativo
- ✅ **Nodo raíz virtual**: "Azure Tenant" cuando no hay Management Groups

#### Layout de Red (Network Mode)  
- ✅ **Contención jerárquica**: RG → VNet → Subnet → Recursos
- ✅ **Multi-subnet support**: NSGs/Route Tables originales + asignaciones
- ✅ **Dimensiones dinámicas**: Contenedores adaptativos al contenido
- ✅ **Layout en arco**: Resource Groups con ≥4 recursos usan semicírculo

#### Iconos y Estilos
- ✅ **Iconos oficiales Azure**: Biblioteca completa img/lib/azure2/
- ✅ **Estilos diferenciados**: Containers, recursos normales, recursos "hidden"
- ✅ **Líneas tipificadas**: Sólidas (jerárquica) vs punteadas (dependencia)

### 🔧 Opciones de Personalización

#### Filtrado por Recursos
```bash
# CLI
--include-ids '/subscriptions/prod-sub /resourceGroups/prod-rg'
--exclude-ids '/subscriptions/dev-sub'

# GitHub Action
include-ids: '/subscriptions/prod-sub /resourceGroups/prod-rg'
exclude-ids: '/subscriptions/dev-sub'
```

#### Filtrado por Tenant
```bash  
# CLI
--tenant-filter 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
--all-tenants

# GitHub Action  
tenant-filter: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
all-tenants: true
```

#### Opciones de Datos
```bash
# CLI
--no-embed-data     # Archivos más ligeros
--export-json       # Exportar datos para análisis

# GitHub Action
no-embed-data: true
export-json: 'azure-inventory.json'
```

### 📋 Siguientes Pasos

#### Visualización en Draw.io
1. 🌐 **Abrir**: Usa [draw.io](https://app.diagrams.net/) 
2. 📐 **Organizar**: Selecciona todo (Ctrl+A) → Menú 'Organizar' → 'Disposición' → 'Gráfico Jerárquico'
3. 🔍 **Explorar**: Click en cualquier recurso + Ctrl+M para ver metadatos
4. 📄 **Navegar**: Usa pestañas inferiores para cambiar entre páginas (modo All)

#### Automatización con GitHub Action
1. 🔧 **Setup**: Sigue [SETUP_GITHUB_ACTION.md](../SETUP_GITHUB_ACTION.md)
2. 📅 **Schedule**: Configura runs automáticos semanales/diarios
3. 📊 **Monitor**: Revisa PRs automáticos con diagramas actualizados
4. 🔄 **Iterate**: Ajusta filtros y configuración según necesidades

### 🏆 Recomendaciones por Caso de Uso

| Caso de Uso | Modo Recomendado | GitHub Action | CLI Local |
|-------------|------------------|---------------|-----------|
| **Informes automáticos** | `all` | ✅ Ideal | ❌ Manual |
| **Auditorías compliance** | `infrastructure` | ✅ Programado | ✅ Ad-hoc |
| **Análisis de red** | `network` | ✅ Cambios | ✅ Troubleshooting |
| **Presentaciones ejecutivas** | `components` | ❌ Overkill | ✅ Perfecto |
| **Documentación viva** | `all` | ✅ PRs automáticos | ❌ Manual |
| **Análisis de costos** | `components` | ✅ Reportes | ✅ Análisis |

---

💡 **Tip**: Para máximo valor, usa el modo `all` con GitHub Action para generar documentación automática completa, y luego usa modos específicos localmente para análisis detallados.
- **≥4 recursos**: Usa disposición radial (círculo)
- **<4 recursos**: Mantiene layout lineal horizontal  
- **Centro inteligente**: Resource Group en el centro del círculo
- **Radio adaptativo**: Se ajusta automáticamente al número de recursos
- **Distribución uniforme**: Ángulos equidistantes entre recursos
- **Conexiones optimizadas**: Líneas radiales desde el centro

**Ventajas visuales:**
- 🎯 **Más compacto**: Reduce significativamente el ancho del diagrama
- 🎨 **Estéticamente superior**: Círculos balanceados y armoniosos  
- 🔍 **Fácil identificación**: RG claramente visible en el centro
- ⚡ **Conexiones cortas**: Líneas radiales más directas
- 📐 **Escalable**: Maneja desde 4 hasta 20+ recursos elegantemente

**Ejemplo visual:**
```
        [VM-1]     [Storage]
           \         /
    [KeyVault] -- [RG] -- [VNet]
           /         \
      [SQL-DB]     [LoadBalancer]
```

**Rendimiento verificado**: 1,290 recursos/segundo con layout radial

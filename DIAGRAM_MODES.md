# Modos de Diagrama - Azure Architecture Diagrams

Este documento describe los diferentes modos de diagrama disponibles en el generador de diagramas de Azure para Draw.io, basados en las recomendaciones de [Microsoft Learn sobre diagramas de diseño de arquitectura](https://learn.microsoft.com/es-es/azure/well-architected/architect-role/design-diagrams).

## Modos Disponibles

### 1. Infrastructure Mode (Por Defecto)
```bash
python src/cli.py --diagram-mode infrastructure
python src/cli.py  # (modo por defecto)
```

**Propósito**: Diagrama de implementación que muestra la jerarquía completa de Azure.

**Características**:
- Representa la estructura real de Azure: Management Groups → Suscripciones → Resource Groups → Recursos
- Disposición como árbol vertical clásico
- Muestra dependencias jerárquicas reales
- Ideal para auditorías, documentación de infraestructura y compliance

**Equivale a**: Diagrama de implementación según Microsoft Learn

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

## Características Visuales Especiales

### Modo Network
- **Contenedores VNet**: Las Virtual Networks se muestran como contenedores rectangulares con bordes punteados (similar a la imagen de referencia)
- **Subnets organizadas**: Las subnets se posicionan dentro de sus VNets como una grilla organizada
- **Recursos dentro de subnets**: Los recursos (VMs, App Services, etc.) se detectan automáticamente y se posicionan dentro de su subnet correspondiente, como en los diagramas oficiales de Azure
- **Tamaños adaptativos**: Los recursos dentro de subnets son más pequeños (60x60) para ajustarse mejor al espacio disponible
- **Detección inteligente**: El sistema intenta asociar recursos con subnets basándose en sus IDs y propiedades
- **Capas claramente separadas**: Cada tipo de recurso se agrupa en su capa correspondiente
- **Estilo Azure oficial**: Los colores y formas siguen las convenciones de los diagramas oficiales de Microsoft

### Todos los Modos
- **Iconos oficiales**: Utiliza los iconos oficiales de Azure cuando están disponibles
- **Metadatos completos**: Cada elemento incluye todos sus datos de Azure (configurable con `--no-embed-data`)
- **Navegación**: Los elementos root incluyen enlaces de exploración interactivos

## Consejos de Uso

1. **Para auditorías y compliance**: Usa `infrastructure` mode
2. **Para presentaciones ejecutivas**: Usa `components` mode  
3. **Para análisis de red**: Usa `network` mode
4. **Para entornos específicos**: Combina con `--include-ids`
5. **Para archivos más ligeros**: Añade `--no-embed-data`

## Personalización

Los modos pueden combinarse con otras opciones:

- `--include-ids`: Filtrar por management groups, suscripciones o resource groups específicos
- `--exclude-ids`: Excluir elementos específicos
- `--no-embed-data`: Generar archivos más ligeros

## Siguiente Paso

Una vez generado el diagrama:

1. Abre el archivo `.drawio` en https://app.diagrams.net
2. Selecciona todo (Ctrl+A)
3. Ve a Menú 'Organizar' → 'Disposición' → 'Gráfico Jerárquico'
4. Ajusta el layout según tus necesidades

## Iconos y Estilos

Todos los modos utilizan los iconos oficiales de Azure cuando están disponibles, siguiendo las recomendaciones de Microsoft para diagramas de arquitectura.

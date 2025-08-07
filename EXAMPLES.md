# Ejemplos de Configuración - Azure Infrastructure Diagrams

Esta guía contiene ejemplos de configuración para diferentes casos de uso tanto con GitHub Actions como con CLI local.

## ⚠️ Nota Importante sobre Autenticación

Todos los ejemplos asumen que ya tienes configurado Azure Login previo en tu workflow. Debes agregar este paso antes de usar la action:

```yaml
- name: Azure Login
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

Para configurar esto, sigue la [guía de configuración](SETUP_GITHUB_ACTION.md).

## 📊 Informes Automáticos

### Reporte Semanal Completo

```yaml
name: Weekly Infrastructure Report
on:
  schedule:
    - cron: '0 6 * * 1'  # Lunes 6 AM UTC
  workflow_dispatch:

permissions:
  id-token: write
  contents: write
  pull-requests: write

jobs:
  weekly-report:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Generate Complete Infrastructure Report
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          diagram-mode: 'all'
          output-path: 'reports/azure-infrastructure-${{ github.run_number }}.drawio'
          export-json: 'reports/azure-inventory-${{ github.run_number }}.json'
          commit-changes: 'pr'
          pr-title: 'Weekly Infrastructure Report #${{ github.run_number }}'
          pr-body: |
            ## 📊 Weekly Azure Infrastructure Report
            
            **Generated**: ${{ github.run_number }}
            **Date**: ${{ github.run_date }}
            
            ### Files
            - Complete diagrams with 4 views (Infrastructure, Components, Network, Network Clean)
            - Raw inventory data for analysis
            
            ### Metrics
            - Resources: ${{ steps.generate.outputs.total-resources }}
            - Dependencies: ${{ steps.generate.outputs.total-dependencies }}
```

### Reporte Diario Ligero

```yaml
name: Daily Infrastructure Check
on:
  schedule:
    - cron: '0 9 * * 1-5'  # Días laborables 9 AM
  workflow_dispatch:

permissions:
  id-token: write
  contents: write

jobs:
  daily-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Generate Light Infrastructure Diagram
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          diagram-mode: 'infrastructure'
          no-embed-data: true  # Archivos más ligeros
          output-path: 'daily/azure-infrastructure-${{ github.run_date }}.drawio'
          commit-changes: 'push'
          target-branch: 'daily-reports'
          commit-message: 'Daily infrastructure check - ${{ github.run_date }}'
```

## 🏢 Entornos Multi-Tenant

### Diagramas Separados por Tenant

```yaml
name: Multi-Tenant Infrastructure Diagrams
on:
  workflow_dispatch:
  schedule:
    - cron: '0 6 * * 1'  # Lunes 6 AM

permissions:
  id-token: write
  contents: write
  pull-requests: write

jobs:
  generate-tenant-diagrams:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        tenant:
          - id: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
            name: 'production'
            subscriptions: '/subscriptions/prod-sub-001 /subscriptions/prod-sub-002'
          - id: 'ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj'
            name: 'development'  
            subscriptions: '/subscriptions/dev-sub-001'
          - id: 'kkkkkkkk-llll-mmmm-nnnn-oooooooooooo'
            name: 'staging'
            subscriptions: '/subscriptions/staging-sub-001'
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ matrix.tenant.id }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Generate Tenant Diagram - ${{ matrix.tenant.name }}
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          tenant-filter: ${{ matrix.tenant.id }}
          include-ids: ${{ matrix.tenant.subscriptions }}
          diagram-mode: 'all'
          output-path: 'tenants/${{ matrix.tenant.name }}-infrastructure.drawio'
          export-json: 'tenants/${{ matrix.tenant.name }}-inventory.json'
          commit-changes: 'pr'
          pr-title: 'Update ${{ matrix.tenant.name }} Infrastructure Diagrams'
```

### Comparación Entre Tenants

```yaml
name: Cross-Tenant Infrastructure Analysis
on:
  workflow_dispatch:
    inputs:
      comparison_tenants:
        description: 'Comma-separated tenant IDs to compare'
        required: true
        default: 'tenant1-id,tenant2-id'

jobs:
  compare-tenants:
    runs-on: ubuntu-latest
    steps:
      - name: Generate All-Tenants Overview
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          # Azure login debe hacerse previamente con azure/login@v2
          all-tenants: true
          diagram-mode: 'components'  # Mejor para comparaciones
          output-path: 'analysis/all-tenants-comparison.drawio'
          export-json: 'analysis/all-tenants-data.json'
          commit-changes: 'pr'
          pr-title: 'Cross-Tenant Infrastructure Analysis'
          pr-body: |
            ## 🔍 Cross-Tenant Infrastructure Analysis
            
            This report compares infrastructure across all tenants.
            
            **Focus**: Components view for better comparison
            **Scope**: All tenants included
            
            Use this to identify:
            - Common patterns across environments
            - Resource type distribution  
            - Cost optimization opportunities
```

## 🌐 Análisis de Red

### Diagrama de Red Simplificado

```yaml
name: Network Topology Analysis
on:
  workflow_dispatch:
    inputs:
      focus_subscription:
        description: 'Subscription ID to focus on'
        required: false
        type: string

jobs:
  network-topology:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Network Topology
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          # Azure login debe hacerse previamente con azure/login@v2
          diagram-mode: 'network'
          no-hierarchy-edges: true  # Solo dependencias funcionales
          include-ids: ${{ inputs.focus_subscription || '' }}
          output-path: 'network/azure-network-topology.drawio'
          commit-changes: 'pr'
          pr-title: 'Network Topology Analysis'
          pr-body: |
            ## 🌐 Network Topology Analysis
            
            **Focus**: Network connectivity and dependencies
            **Filtering**: Functional dependencies only (no hierarchical clutter)
            
            This diagram shows:
            - VNet and subnet organization
            - Network security groups and routing
            - Connectivity dependencies
            - Multi-subnet resource assignments
```

### Análisis de Seguridad de Red

```yaml
name: Network Security Analysis  
on:
  workflow_dispatch:
  schedule:
    - cron: '0 10 * * 2'  # Martes 10 AM (día después del reporte semanal)

jobs:
  security-analysis:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Security-Focused Network Diagram
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          # Azure login debe hacerse previamente con azure/login@v2
          diagram-mode: 'network'
          # Incluir solo recursos relacionados con seguridad de red
          output-path: 'security/network-security-analysis.drawio'
          export-json: 'security/network-security-data.json'
          commit-changes: 'pr'
          pr-title: 'Network Security Analysis'
```

## 🔍 Detección de Cambios

### Monitoreo Continuo

```yaml
name: Infrastructure Change Detection
on:
  schedule:
    - cron: '0 */4 * * *'  # Cada 4 horas
  workflow_dispatch:

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout for baseline
        uses: actions/checkout@v4
        with:
          path: 'current'
      
      - name: Generate Current State
        id: current-state
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          # Azure login debe hacerse previamente con azure/login@v2
          export-json: 'current-state.json'
          commit-changes: 'none'  # Solo generar, no commitear aún
      
      - name: Compare with Baseline
        id: compare
        run: |
          if [ -f "current/baseline-state.json" ]; then
            # Script de comparación personalizado
            python scripts/compare_infrastructure.py \
              current/baseline-state.json \
              current-state.json \
              --output changes-detected.json
            
            # Verificar si hay cambios significativos
            CHANGES=$(jq '.significant_changes' changes-detected.json)
            echo "has-changes=$CHANGES" >> $GITHUB_OUTPUT
          else
            echo "has-changes=true" >> $GITHUB_OUTPUT
            echo "No baseline found, treating as changes"
          fi
      
      - name: Update Infrastructure Diagrams on Changes
        if: steps.compare.outputs.has-changes == 'true'
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          # Azure login debe hacerse previamente con azure/login@v2
          diagram-mode: 'all'
          output-path: 'infrastructure/azure-infrastructure-updated.drawio'
          commit-changes: 'pr'
          pr-title: '🚨 Infrastructure Changes Detected'
          pr-body: |
            ## 🚨 Infrastructure Changes Detected
            
            **Trigger**: Automated monitoring detected changes
            **Last Check**: ${{ github.run_started_at }}
            
            ### Actions Taken
            - Generated updated infrastructure diagrams
            - Exported current state for analysis
            
            ### Next Steps
            1. Review the changes in the diagram
            2. Validate if changes are expected
            3. Update documentation if needed
      
      - name: Store Current as New Baseline
        if: steps.compare.outputs.has-changes == 'true'
        run: |
          cp current-state.json current/baseline-state.json
          cd current
          git config user.name 'Infrastructure Monitor'
          git config user.email 'action@github.com'
          git add baseline-state.json
          git commit -m "Update infrastructure baseline - ${{ github.run_started_at }}"
          git push
```

## 🏗️ Por Tipo de Proyecto

### Proyecto con Microservicios

```yaml
name: Microservices Infrastructure
on:
  workflow_dispatch:
  push:
    paths:
      - 'infrastructure/**'  # Trigger en cambios de infraestructura

jobs:
  microservices-diagram:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Microservices Infrastructure
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          # Azure login debe hacerse previamente con azure/login@v2
          diagram-mode: 'network'  # Enfoque en conectividad entre servicios
          include-ids: '/subscriptions/microservices-prod /subscriptions/microservices-staging'
          no-hierarchy-edges: true
          output-path: 'docs/microservices-topology.drawio'
          commit-changes: 'push'
          target-branch: 'main'
          commit-message: 'Update microservices infrastructure topology'
```

### Proyecto de Data Platform

```yaml
name: Data Platform Infrastructure
on:
  workflow_dispatch:
  schedule:
    - cron: '0 7 * * *'  # Diario 7 AM

jobs:
  data-platform:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Data Platform Diagram
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          # Azure login debe hacerse previamente con azure/login@v2
          diagram-mode: 'components'  # Enfoque en servicios de datos
          include-ids: '/resourceGroups/data-platform-prod /resourceGroups/data-lake-prod'
          output-path: 'docs/data-platform-architecture.drawio'
          export-json: 'docs/data-platform-inventory.json'
          commit-changes: 'pr'
          pr-title: 'Data Platform Architecture Update'
```

## 📋 Uso Local (CLI)

### Desarrollo y Testing

```bash
# Análisis rápido durante desarrollo
python src/cli.py --diagram-mode infrastructure --include-ids "/subscriptions/dev-sub" --output dev-check.drawio

# Análisis de red para troubleshooting
python src/cli.py --diagram-mode network --no-hierarchy-edges --include-ids "/resourceGroups/network-rg" --output network-debug.drawio

# Exportar datos para análisis personalizado
python src/cli.py --export-json dev-inventory.json --include-ids "/subscriptions/dev-sub"

# Generar diagrama desde datos offline
python src/cli.py --input-json dev-inventory.json --diagram-mode components --output dev-components.drawio
```

### Análisis por Tenant Local

```bash
# Obtener lista de tenants disponibles
python src/cli.py --list-tenants

# Generar diagrama para tenant específico
python src/cli.py --tenant-filter "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee" --output tenant-a.drawio

# Incluir todos los tenants
python src/cli.py --all-tenants --diagram-mode all --output all-tenants-complete.drawio

# Comparar tenants generando archivos separados
python src/cli.py --tenant-filter "tenant-1-id" --export-json tenant1.json
python src/cli.py --tenant-filter "tenant-2-id" --export-json tenant2.json
```

### Casos de Uso Específicos

```bash
# Solo recursos de producción
python src/cli.py --include-ids "/subscriptions/prod-sub-001 /subscriptions/prod-sub-002" --output production-only.drawio

# Excluir recursos de desarrollo y test
python src/cli.py --exclude-ids "/subscriptions/dev-sub /subscriptions/test-sub" --output non-dev-resources.drawio

# Diagrama ligero sin datos embebidos
python src/cli.py --no-embed-data --output lightweight-diagram.drawio

# Análisis de red específico con filtrado
python src/cli.py --diagram-mode network --no-hierarchy-edges --include-ids "/resourceGroups/networking-prod" --output network-analysis.drawio
```

## 🔧 Configuración Avanzada de Secretos

### Múltiples Service Principals

```yaml
# En GitHub Secrets, crear:
# AZURE_CREDENTIALS_PROD
# AZURE_CREDENTIALS_DEV  
# AZURE_CREDENTIALS_STAGING

name: Multi-Environment Diagrams
on:
  workflow_dispatch:

jobs:
  multi-env:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [production, development, staging]
        include:
          - environment: production
            credentials: AZURE_CREDENTIALS_PROD
            output: prod-infrastructure.drawio
          - environment: development
            credentials: AZURE_CREDENTIALS_DEV
            output: dev-infrastructure.drawio
          - environment: staging
            credentials: AZURE_CREDENTIALS_STAGING
            output: staging-infrastructure.drawio
    
    steps:
      - name: Generate ${{ matrix.environment }} Infrastructure
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          # Azure login debe hacerse previamente con azure/login@v2
          diagram-mode: 'all'
          output-path: 'environments/${{ matrix.output }}'
          commit-changes: 'push'
```

### Configuración con Variables de Entorno

```yaml
name: Environment-Based Configuration
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options: [production, staging, development]

env:
  PROD_SUBSCRIPTION: '/subscriptions/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
  STAGING_SUBSCRIPTION: '/subscriptions/ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj'
  DEV_SUBSCRIPTION: '/subscriptions/kkkkkkkk-llll-mmmm-nnnn-oooooooooooo'

jobs:
  generate-diagram:
    runs-on: ubuntu-latest
    steps:
      - name: Set Environment Variables
        run: |
          case "${{ inputs.environment }}" in
            production)
              echo "TARGET_SUBSCRIPTION=${{ env.PROD_SUBSCRIPTION }}" >> $GITHUB_ENV
              echo "OUTPUT_PATH=docs/production-infrastructure.drawio" >> $GITHUB_ENV
              ;;
            staging)
              echo "TARGET_SUBSCRIPTION=${{ env.STAGING_SUBSCRIPTION }}" >> $GITHUB_ENV
              echo "OUTPUT_PATH=docs/staging-infrastructure.drawio" >> $GITHUB_ENV
              ;;
            development)
              echo "TARGET_SUBSCRIPTION=${{ env.DEV_SUBSCRIPTION }}" >> $GITHUB_ENV
              echo "OUTPUT_PATH=docs/development-infrastructure.drawio" >> $GITHUB_ENV
              ;;
          esac
      
      - name: Generate Environment Diagram
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          # Azure login debe hacerse previamente con azure/login@v2
          include-ids: ${{ env.TARGET_SUBSCRIPTION }}
          diagram-mode: 'all'
          output-path: ${{ env.OUTPUT_PATH }}
          commit-changes: 'pr'
          pr-title: 'Update ${{ inputs.environment }} Infrastructure Diagram'
```

---

💡 **Tip**: Combina estos ejemplos según tus necesidades específicas. Comienza con configuraciones simples y añade complejidad gradualmente.

# Configuración de Azure Infrastructure Diagrams como GitHub Action

Esta guía te ayudará a configurar la GitHub Action para generar automáticamente diagramas de tu infraestructura Azure.

## 🚀 Configuración Rápida (5 minutos)

### Paso 1: Configurar Azure Application/Service Principal

```bash
# Crear aplicación Azure AD
az ad app create --display-name "GitHub-Azure-Infrastructure-Diagrams"

# Obtener el App ID
APP_ID=$(az ad app list --display-name "GitHub-Azure-Infrastructure-Diagrams" --query '[0].appId' -o tsv)

# Crear service principal
az ad sp create --id $APP_ID

# Asignar permisos de lectura
az role assignment create \
  --assignee $APP_ID \
  --role "Reader" \
  --scope "/subscriptions/{TU_SUBSCRIPTION_ID}"

# Configurar federated credentials para GitHub
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-actions",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:OWNER/REPO:ref:refs/heads/main",
    "description": "GitHub Actions",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

**Nota**: Reemplaza `OWNER/REPO` con tu usuario/organización y nombre del repositorio.

### Paso 2: Configurar Secretos en GitHub

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Crea estos secretos:
   - **Name**: `AZURE_CLIENT_ID` **Value**: El App ID del paso anterior
   - **Name**: `AZURE_TENANT_ID` **Value**: Tu Tenant ID de Azure
   - **Name**: `AZURE_SUBSCRIPTION_ID` **Value**: Tu Subscription ID

### Paso 3: Crear Workflow

Crea el archivo `.github/workflows/azure-diagrams.yml`:

```yaml
name: Azure Infrastructure Diagrams
on:
  workflow_dispatch:
  schedule:
    - cron: '0 6 * * 1'  # Lunes 6 AM

permissions:
  id-token: write   # Required for OIDC
  contents: read    # Required for checkout

jobs:
  generate:
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

      - name: Generate Infrastructure Diagram
        uses: rfernandezdo/inventariographdrawio@v1
        with:
          diagram-mode: 'all'
          output-path: 'docs/azure-infrastructure.drawio'
          commit-changes: 'pr'
```

### Paso 4: Ejecutar

1. Ve a **Actions** en tu repositorio
2. Selecciona "Azure Infrastructure Diagrams"
3. Clic en **Run workflow**
4. ¡Espera tu Pull Request automático! 🎉

## 📋 Configuraciones Avanzadas

### Multi-Tenant

```yaml
# Diagrama para tenant específico
- name: Azure Login
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

- name: Generate Tenant Diagram
  uses: rfernandezdo/inventariographdrawio@v1
  with:
    tenant-filter: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    output-path: 'docs/tenant-a-infrastructure.drawio'

# Todos los tenants
- name: Generate All Tenants Diagram
  uses: rfernandezdo/inventariographdrawio@v1
  with:
    all-tenants: true
    output-path: 'docs/all-tenants-infrastructure.drawio'
```

### Filtrado por Recursos

```yaml
# Solo recursos de producción
- name: Azure Login
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

- name: Generate Production Diagram
  uses: rfernandezdo/inventariographdrawio@v1
  with:
    include-ids: '/subscriptions/prod-subscription-id /resourceGroups/prod-rg'
    output-path: 'docs/production-only.drawio'

# Excluir recursos de desarrollo
- name: Generate Without Dev Diagram
  uses: rfernandezdo/inventariographdrawio@v1
  with:
    exclude-ids: '/subscriptions/dev-subscription-id'
    output-path: 'docs/without-dev.drawio'
```

### Diferentes Modos de Commit

```yaml
# Push directo a main
commit-changes: 'push'
target-branch: 'main'

# Crear Pull Request
commit-changes: 'pr'
pr-title: 'Update Infrastructure Diagrams'
pr-body: 'Automated update from Azure resources'

# Solo generar archivos (sin commit)
commit-changes: 'none'
```

## 🔧 Opciones Completas

| Parámetro | Descripción | Requerido | Defecto |
|-----------|-------------|-----------|---------|
| `diagram-mode` | Tipo: `infrastructure`, `components`, `network`, `all` | ❌ | `infrastructure` |
| `output-path` | Ruta del archivo .drawio | ❌ | `azure-infrastructure-diagram.drawio` |
| `tenant-filter` | ID del tenant específico | ❌ | - |
| `all-tenants` | Incluir todos los tenants | ❌ | `false` |
| `no-embed-data` | No incrustar datos completos | ❌ | `false` |
| `no-hierarchy-edges` | Sin enlaces jerárquicos (modo network) | ❌ | `false` |
| `include-ids` | IDs a incluir (separados por espacio) | ❌ | - |
| `exclude-ids` | IDs a excluir (separados por espacio) | ❌ | - |
| `export-json` | Exportar datos a JSON | ❌ | - |
| `commit-changes` | Acción: `none`, `push`, `pr` | ❌ | `none` |
| `target-branch` | Rama destino | ❌ | `main` |
| `pr-title` | Título del PR | ❌ | `Update Azure Infrastructure Diagrams` |
| `pr-body` | Descripción del PR | ❌ | Auto-generado |
| `commit-message` | Mensaje del commit | ❌ | `Update Azure infrastructure diagrams` |

## 📊 Salidas (Outputs)

```yaml
- name: Azure Login
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

- name: Generate Diagrams
  id: generate
  uses: rfernandezdo/inventariographdrawio@v1
  with:
    diagram-mode: 'all'

- name: Use Outputs
  run: |
    echo "Diagram: ${{ steps.generate.outputs.diagram-path }}"
    echo "Resources: ${{ steps.generate.outputs.total-resources }}"
    echo "Dependencies: ${{ steps.generate.outputs.total-dependencies }}"
    echo "Tenant: ${{ steps.generate.outputs.tenant-id }}"
    echo "PR Number: ${{ steps.generate.outputs.pr-number }}"
    echo "Commit SHA: ${{ steps.generate.outputs.commit-sha }}"
```

## 🛡️ Seguridad y Permisos

### Permisos Azure Requeridos

```bash
# Obtener el Application ID creado en el Paso 1
APP_ID=$(az ad app list --display-name "GitHub-Azure-Infrastructure-Diagrams" --query '[0].appId' -o tsv)

# Mínimo: Reader en suscripciones que quieres diagramar
az role assignment create \
  --assignee $APP_ID \
  --role "Reader" \
  --scope "/subscriptions/{SUBSCRIPTION_ID}"

# Para múltiples suscripciones:
az role assignment create \
  --assignee $APP_ID \
  --role "Reader" \
  --scope "/managementGroups/{MANAGEMENT_GROUP_ID}"
```

### Permisos GitHub Requeridos

En tu workflow, asegúrate de tener los permisos necesarios:

```yaml
permissions:
  id-token: write        # Requerido para OIDC
  contents: write        # Para commits
  pull-requests: write   # Para crear PRs
  issues: write          # Para crear issues (opcional)
```

### Datos Sensibles

- ✅ **La action no expone datos sensibles** en logs
- ✅ **Solo usa permisos de lectura** en Azure
- ✅ **Usa OIDC (sin secretos)** para autenticación segura
- ✅ **No envía datos a servicios externos**
- ✅ **Los diagramas se quedan en tu repositorio**

## 🔍 Resolución de Problemas

### Error: "Azure Login failed"

1. **Verifica que los secretos estén configurados correctamente:**
   - `AZURE_CLIENT_ID`
   - `AZURE_TENANT_ID`
   - `AZURE_SUBSCRIPTION_ID`

2. **Verifica que el federated credential esté configurado:**
```bash
# Listar federated credentials
az ad app federated-credential list --id $APP_ID
```

3. **Verifica permisos OIDC en el workflow:**
```yaml
permissions:
  id-token: write
  contents: read
  "tenantId": "..."
}
```

### Error: "No se encontraron elementos"

1. **Verifica permisos**: El service principal necesita rol "Reader"
2. **Revisa scope**: ¿Está asignado a las suscripciones correctas?
3. **Chequea tenant**: ¿Estás filtrando el tenant correcto?

### Error: "Permission denied"

```yaml
# Añade permisos al workflow
permissions:
  contents: write
  pull-requests: write
```

### Timeout en infraestructuras grandes

```yaml
# Usa filtros para reducir el scope
include-ids: '/subscriptions/specific-subscription'
no-embed-data: true  # Reduce el tamaño del archivo
```

## 📈 Casos de Uso Recomendados

### 1. Informes Semanales Automáticos

```yaml
name: Weekly Infrastructure Report
on:
  schedule:
    - cron: '0 6 * * 1'  # Lunes 6 AM

permissions:
  id-token: write
  contents: write
  pull-requests: write

jobs:
  report:
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

      - name: Generate Infrastructure Report
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          diagram-mode: 'all'
          export-json: 'reports/azure-inventory-${{ github.run_number }}.json'
          output-path: 'reports/azure-diagrams-${{ github.run_number }}.drawio'
          commit-changes: 'pr'
          pr-title: 'Weekly Infrastructure Report #${{ github.run_number }}'
```

### 2. Detección de Cambios

```yaml
name: Infrastructure Changes
on:
  schedule:
    - cron: '0 */6 * * *'  # Cada 6 horas

permissions:
  id-token: write
  contents: write
  issues: write

jobs:
  detect:
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
      
      - name: Generate Current Snapshot
        id: current
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          export-json: 'current.json'
          commit-changes: 'none'
      
      - name: Compare with Previous
        run: |
          # Script para comparar current.json con previous.json
          # y crear issue si hay cambios
```

### 3. Documentación por Entorno

```yaml
name: Multi-Environment Docs
on:
  workflow_dispatch:

permissions:
  id-token: write
  contents: write

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [production, staging, development]
        include:
          - environment: production
            tenant: 'prod-tenant-id'
            subscription: '/subscriptions/prod-sub-id'
          - environment: staging  
            tenant: 'staging-tenant-id'
            subscription: '/subscriptions/staging-sub-id'
          - environment: development
            tenant: 'dev-tenant-id'
            subscription: '/subscriptions/dev-sub-id'
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Azure Login for ${{ matrix.environment }}
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ matrix.tenant }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Generate ${{ matrix.environment }} Diagram
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          tenant-filter: ${{ matrix.tenant }}
          include-ids: ${{ matrix.subscription }}
          output-path: 'docs/${{ matrix.environment }}-infrastructure.drawio'
          commit-changes: 'push'
```

## 🎯 Tips y Mejores Prácticas

### Performance

- ✅ **Usa `no-embed-data: true`** para diagramas más ligeros
- ✅ **Filtra por subscription** para entornos grandes
- ✅ **Programa runs en horarios de bajo uso**

### Organización

- ✅ **Usa nombres descriptivos** para archivos de salida
- ✅ **Organiza por carpetas**: `docs/`, `reports/`, etc.
- ✅ **Versionado con fechas**: `azure-diagrams-${{ github.run_number }}.drawio`

### Colaboración

- ✅ **Crea PRs automáticos** para revisión en equipo
- ✅ **Incluye métricas** en descripciones de PR
- ✅ **Notifica en Teams/Slack** cuando hay cambios

### Monitoreo

- ✅ **Configura alertas** para cambios inesperados
- ✅ **Mantén historial** de diagramas anteriores
- ✅ **Documenta cambios** importantes

## 📚 Recursos Adicionales

- 🎨 [Draw.io Online](https://app.diagrams.net/)
- 📖 [Azure Resource Graph Docs](https://docs.microsoft.com/en-us/azure/governance/resource-graph/)
- 🔧 [GitHub Actions Docs](https://docs.github.com/en/actions)
- 🤖 [Action en GitHub Marketplace](https://github.com/marketplace/actions/azure-infrastructure-diagrams-for-draw-io)

---

¿Necesitas ayuda? [Crea un issue](https://github.com/rfernandezdo/inventariographdrawio/issues) con tus preguntas.

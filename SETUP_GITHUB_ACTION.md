# Configuración de Azure Infrastructure Diagrams como GitHub Action

Esta guía te ayudará a configurar la GitHub Action para generar automáticamente diagramas de tu infraestructura Azure.

## 🚀 Configuración Rápida (5 minutos)

### Paso 1: Crear Service Principal en Azure

```bash
# Crear service principal con permisos de lectura
az ad sp create-for-rbac \
  --name "GitHub-Azure-Infrastructure-Diagrams" \
  --role "Reader" \
  --scopes /subscriptions/{TU_SUBSCRIPTION_ID} \
  --sdk-auth
```

**Guarda la salida JSON** - la necesitarás en el siguiente paso.

### Paso 2: Configurar Secreto en GitHub

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Clic en **New repository secret**
4. **Name**: `AZURE_CREDENTIALS`
5. **Value**: Pega el JSON completo del paso anterior
6. Clic en **Add secret**

### Paso 3: Crear Workflow

Crea el archivo `.github/workflows/azure-diagrams.yml`:

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
- uses: rfernandezdo/inventariographdrawio@v1
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
    tenant-filter: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    output-path: 'docs/tenant-a-infrastructure.drawio'

# Todos los tenants
- uses: rfernandezdo/inventariographdrawio@v1
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
    all-tenants: true
    output-path: 'docs/all-tenants-infrastructure.drawio'
```

### Filtrado por Recursos

```yaml
# Solo recursos de producción
- uses: rfernandezdo/inventariographdrawio@v1
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
    include-ids: '/subscriptions/prod-subscription-id /resourceGroups/prod-rg'
    output-path: 'docs/production-only.drawio'

# Excluir recursos de desarrollo
- uses: rfernandezdo/inventariographdrawio@v1
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
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
| `azure-credentials` | Credenciales del service principal (JSON) | ✅ | - |
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
- name: Generate Diagrams
  id: generate
  uses: rfernandezdo/inventariographdrawio@v1
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}

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
# Mínimo: Reader en suscripciones que quieres diagramar
az role assignment create \
  --assignee {SERVICE_PRINCIPAL_ID} \
  --role "Reader" \
  --scope "/subscriptions/{SUBSCRIPTION_ID}"

# Para múltiples suscripciones:
az role assignment create \
  --assignee {SERVICE_PRINCIPAL_ID} \
  --role "Reader" \
  --scope "/managementGroups/{MANAGEMENT_GROUP_ID}"
```

### Permisos GitHub Requeridos

En tu workflow, asegúrate de tener los permisos necesarios:

```yaml
permissions:
  contents: write        # Para commits
  pull-requests: write   # Para crear PRs
  issues: write          # Para crear issues (opcional)
```

### Datos Sensibles

- ✅ **La action no expone datos sensibles** en logs
- ✅ **Solo usa permisos de lectura** en Azure
- ✅ **No envía datos a servicios externos**
- ✅ **Los diagramas se quedan en tu repositorio**

## 🔍 Resolución de Problemas

### Error: "Az CLI Login failed"

```yaml
# Verifica el formato del secreto AZURE_CREDENTIALS
{
  "clientId": "...",
  "clientSecret": "...", 
  "subscriptionId": "...",
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

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: rfernandezdo/inventariographdrawio@v1
        with:
          azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
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

jobs:
  detect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: rfernandezdo/inventariographdrawio@v1
        id: current
        with:
          azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
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
      - uses: rfernandezdo/inventariographdrawio@v1
        with:
          azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
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

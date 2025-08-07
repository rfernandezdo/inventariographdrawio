# Azure Infrastructure Diagrams for Draw.io - GitHub Action

A GitHub Action that automatically generates dynamic Azure infrastructure diagrams from your real Azure resources using Azure Resource Graph API and exports them as draw.io files.

## Features

🌳 **Hierarchical Infrastructure Visualization**: Complete hierarchy from Management Groups → Subscriptions → Resource Groups → Resources  
📊 **Multiple Diagram Modes**: Infrastructure, Components, Network, and All-in-one multi-page diagrams  
🏢 **Multi-Tenant Support**: Filter by specific tenant or include all tenants  
⚡ **High Performance**: Handles 1000+ resources in under 2 seconds  
🎯 **Smart Filtering**: Include/exclude specific resources by ID  
🔄 **Automated Updates**: Push diagrams to branches or create pull requests  
📱 **Export Options**: Generate both draw.io files and JSON exports  

## ⚠️ Authentication Requirements

This action requires Azure authentication to be configured **before** using it. You must use `azure/login@v2` in your workflow:

```yaml
- name: Azure Login
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

**Migration from v0.x**: If you were using `azure-credentials` input in previous versions, please follow the [setup guide](SETUP_GITHUB_ACTION.md) to migrate to OIDC authentication.  

## Quick Start

```yaml
name: Generate Azure Infrastructure Diagrams
on:
  workflow_dispatch:
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday at 6 AM

permissions:
  id-token: write
  contents: write
  pull-requests: write

jobs:
  generate-diagrams:
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
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          diagram-mode: 'all'
          output-path: 'docs/azure-infrastructure.drawio'
          commit-changes: 'pr'
          pr-title: 'Update Azure Infrastructure Diagrams'
```

## Inputs

### Optional Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `diagram-mode` | Type of diagram: `infrastructure`, `components`, `network`, `all` | ❌ | `infrastructure` |
| `output-path` | Path for the generated draw.io file | ❌ | `azure-infrastructure-diagram.drawio` |
| `tenant-filter` | Filter resources by specific Tenant ID | ❌ | - |
| `all-tenants` | Include resources from all tenants | ❌ | `false` |
| `no-embed-data` | Do not embed all data in nodes | ❌ | `false` |
| `no-hierarchy-edges` | Hide hierarchical edges in network mode | ❌ | `false` |
| `include-ids` | Space-separated list of IDs to include | ❌ | - |
| `exclude-ids` | Space-separated list of IDs to exclude | ❌ | - |
| `export-json` | Export data to JSON file | ❌ | - |
| `commit-changes` | Commit behavior: `none`, `push`, `pr` | ❌ | `none` |
| `target-branch` | Target branch for commits | ❌ | `main` |
| `pr-title` | Pull request title | ❌ | `Update Azure Infrastructure Diagrams` |
| `pr-body` | Pull request body | ❌ | Auto-generated |
| `commit-message` | Commit message | ❌ | `Update Azure infrastructure diagrams` |

## Outputs

| Output | Description |
|--------|-------------|
| `diagram-path` | Path to the generated draw.io diagram file |
| `json-export-path` | Path to the exported JSON file (if applicable) |
| `total-resources` | Total number of resources found |
| `total-dependencies` | Total number of dependencies found |
| `tenant-id` | Tenant ID used for filtering |
| `pr-number` | Pull request number (if PR was created) |
| `commit-sha` | Commit SHA of the changes |

## Setup Azure Credentials

1. Create an Azure Service Principal:
```bash
az ad sp create-for-rbac --name "GitHub-Azure-Infrastructure-Diagrams" --role "Reader" --scopes /subscriptions/{subscription-id} --sdk-auth
```

2. Add the output as a repository secret named `AZURE_CREDENTIALS`:
```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "..."
}
```

## Diagram Modes

### 🌳 Infrastructure Mode (Default - Recommended)
Complete hierarchical structure showing the full Azure organization:
- Management Groups → Subscriptions → Resource Groups → Resources
- DFS (Depth-First Search) tree layout
- Supports 25+ Azure resource types
- Handles 1000+ resources efficiently

### 📦 Components Mode
Groups resources by function and type:
- Compute, Storage, Network, Database, Security, AI/ML categories
- Functional organization for architecture analysis

### 🌐 Network Mode
Focused on network topology and connectivity:
- VNets, Subnets, Gateways, Firewalls
- Multi-subnet support for NSGs and Route Tables
- Network dependency visualization

### 📄 All Mode (Multi-page)
All diagram types in a single draw.io file with separate pages:
- Page 1: Infrastructure (complete hierarchy)
- Page 2: Components (grouped by function)
- Page 3: Network (with hierarchical edges)
- Page 4: Network Clean (functional dependencies only)

## Usage Examples

### Basic Infrastructure Diagram
```yaml
- name: Generate Basic Infrastructure Diagram
  uses: rfernandezdo/inventariographdrawio@v2
  with:
    # Azure login debe hacerse previamente con azure/login@v2
    output-path: 'diagrams/infrastructure.drawio'
```

### Multi-page Diagram with PR
```yaml
- name: Generate All Diagrams and Create PR
  uses: rfernandezdo/inventariographdrawio@v2
  with:
    # Azure login debe hacerse previamente con azure/login@v2
    diagram-mode: 'all'
    output-path: 'docs/azure-complete.drawio'
    export-json: 'docs/azure-inventory.json'
    commit-changes: 'pr'
    pr-title: 'Weekly Azure Infrastructure Update'
    pr-body: |
      ## 📊 Azure Infrastructure Update
      
      This PR contains the weekly update of our Azure infrastructure diagrams.
      
      ### Generated Files:
      - **Complete Diagrams**: Multi-page view with all visualization modes
      - **JSON Export**: Raw data for further analysis
      
      ### Summary:
      - Total Resources: ${{ steps.generate.outputs.total-resources }}
      - Total Dependencies: ${{ steps.generate.outputs.total-dependencies }}
      - Tenant: ${{ steps.generate.outputs.tenant-id }}
```

### Network-focused Diagram for Specific Resources
```yaml
- name: Generate Network Diagram for Production
  uses: rfernandezdo/inventariographdrawio@v2
  with:
    # Azure login debe hacerse previamente con azure/login@v2
    diagram-mode: 'network'
    include-ids: '/subscriptions/prod-subscription-id'
    no-hierarchy-edges: true
    output-path: 'network/production-topology.drawio'
    commit-changes: 'push'
    target-branch: 'network-docs'
```

### Multi-tenant Environment
```yaml
- name: Generate Separate Diagrams per Tenant
  uses: rfernandezdo/inventariographdrawio@v2
  with:
    # Azure login debe hacerse previamente con azure/login@v2
    tenant-filter: ${{ matrix.tenant }}
    output-path: 'diagrams/${{ matrix.tenant-name }}-infrastructure.drawio'
    commit-changes: 'push'
  strategy:
    matrix:
      include:
        - tenant: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
          tenant-name: 'production'
        - tenant: 'ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj'
          tenant-name: 'development'
```

## Automated Workflows

### Weekly Infrastructure Reports
```yaml
name: Weekly Infrastructure Reports
on:
  schedule:
    - cron: '0 6 * * 1'  # Monday 6 AM

jobs:
  generate-reports:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Infrastructure Report
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          # Azure login debe hacerse previamente con azure/login@v2
          diagram-mode: 'all'
          export-json: 'reports/azure-inventory-${{ github.run_number }}.json'
          output-path: 'reports/azure-infrastructure-${{ github.run_number }}.drawio'
          commit-changes: 'pr'
          pr-title: 'Weekly Infrastructure Report #${{ github.run_number }}'
      
      - name: Archive Reports
        uses: actions/upload-artifact@v3
        with:
          name: azure-infrastructure-reports
          path: reports/
```

### Infrastructure Change Detection
```yaml
name: Infrastructure Change Detection
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Current Infrastructure
        id: current
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          # Azure login debe hacerse previamente con azure/login@v2
          export-json: 'current-inventory.json'
          commit-changes: 'none'
      
      - name: Compare with Previous
        run: |
          if [ -f "previous-inventory.json" ]; then
            # Compare JSON files and create summary
            python scripts/compare-inventories.py previous-inventory.json current-inventory.json > changes-summary.md
          fi
      
      - name: Create Issue if Changes Detected
        if: steps.compare.outputs.changes-detected == 'true'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Azure Infrastructure Changes Detected',
              body: require('fs').readFileSync('changes-summary.md', 'utf8')
            });
```

## Resource Requirements

- **Azure Permissions**: `Reader` role on subscriptions/management groups
- **GitHub Permissions**: `contents: write` and `pull-requests: write` (for commit-changes)
- **Runtime**: ~2-5 minutes for typical infrastructures (depends on resource count)
- **Storage**: ~1-10MB per diagram (depends on resource count and embed-data setting)

## Security Considerations

- **Sensitive Data**: Action filters sensitive information from outputs
- **Credentials**: Use GitHub secrets for Azure credentials
- **Permissions**: Follows principle of least privilege (Reader role only)
- **Data Privacy**: No data is sent to external services (runs entirely in GitHub Actions)

## Troubleshooting

### Common Issues

**Azure Login Failed**
```
Error: Az CLI Login failed. Please check the credentials.
```
- Verify `AZURE_CREDENTIALS` secret format
- Ensure service principal has correct permissions
- Check if tenant ID is correct

**No Resources Found**
```
AVISO: No se encontraron elementos. Revisa tu login ('az login') y permisos.
```
- Verify Azure permissions (Reader role required)
- Check if tenant-filter is excluding all resources
- Ensure Azure CLI and resource-graph extension are properly installed

**Large Infrastructure Timeout**
- Use `include-ids` to process specific subscriptions/resource groups
- Consider running separate workflows for different tenants
- Use `no-embed-data: true` to reduce file size

### Debug Mode

Enable debug output by adding:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
```

## Contributing

This action is built on the [inventariographdrawio](https://github.com/rfernandezdo/inventariographdrawio) project. 

For feature requests or bug reports:
1. Check existing [issues](https://github.com/rfernandezdo/inventariographdrawio/issues)
2. Create a new issue with detailed description
3. Include sample Azure resource configuration if applicable

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Azure Resource Graph](https://docs.microsoft.com/en-us/azure/governance/resource-graph/) - Microsoft's service for querying Azure resources
- [Draw.io](https://draw.io) - Free online diagram software
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/) - Command-line interface for Azure

---

**🎯 Perfect for**: Infrastructure documentation, compliance reporting, architecture reviews, and automated documentation pipelines.

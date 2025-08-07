# Migration Guide: v1.x to v2.0

## 🚨 Breaking Changes in v2.0

Version 2.0 introduces **OIDC authentication** for enhanced security, requiring migration from the previous `azure-credentials` approach.

## What Changed

### ❌ Removed
- `azure-credentials` input parameter
- Support for service principal JSON secrets

### ✅ Added  
- Requirement for `azure/login@v2` step
- OIDC (OpenID Connect) authentication
- Enhanced security without long-lived secrets

## Migration Steps

### Step 1: Update Azure Configuration

**Old Setup (Service Principal with Secrets)**:
```bash
az ad sp create-for-rbac --name "GitHub-Action" --role "Reader" --scopes /subscriptions/{id} --sdk-auth
```

**New Setup (OIDC)**:
```bash
# Create Azure AD app
az ad app create --display-name "GitHub-Azure-Infrastructure-Diagrams"
APP_ID=$(az ad app list --display-name "GitHub-Azure-Infrastructure-Diagrams" --query '[0].appId' -o tsv)

# Create service principal
az ad sp create --id $APP_ID

# Assign Reader role
az role assignment create --assignee $APP_ID --role "Reader" --scope "/subscriptions/{SUBSCRIPTION_ID}"

# Configure federated credential for GitHub
az ad app federated-credential create --id $APP_ID --parameters '{
  "name": "github-actions",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:OWNER/REPO:ref:refs/heads/main",
  "description": "GitHub Actions",
  "audiences": ["api://AzureADTokenExchange"]
}'
```

### Step 2: Update GitHub Secrets

**Remove**: 
- `AZURE_CREDENTIALS` secret

**Add**:
- `AZURE_CLIENT_ID` (the App ID from step 1)
- `AZURE_TENANT_ID` (your Azure Tenant ID)
- `AZURE_SUBSCRIPTION_ID` (your Azure Subscription ID)

### Step 3: Update Workflows

**Before (v1.x)**:
```yaml
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: rfernandezdo/inventariographdrawio@v2
        with:
          azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
          diagram-mode: 'all'
```

**After (v2.0)**:
```yaml
jobs:
  generate:
    runs-on: ubuntu-latest
    
    permissions:
      id-token: write  # Required for OIDC
      contents: write  # Required for file operations
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Generate Diagrams
        uses: rfernandezdo/inventariographdrawio@v2
        with:
          diagram-mode: 'all'
```

## Benefits of v2.0

✅ **Enhanced Security**: No more long-lived secrets  
✅ **OIDC Standard**: Industry-standard authentication  
✅ **Azure Native**: Uses Azure's recommended authentication method  
✅ **Automatic Rotation**: Tokens are automatically rotated  
✅ **Reduced Attack Surface**: Shorter-lived credentials  

## Need Help?

- 📖 [Complete Setup Guide](SETUP_GITHUB_ACTION.md)
- 💡 [Examples](EXAMPLES.md)
- 🐛 [Open an Issue](https://github.com/rfernandezdo/inventariographdrawio/issues)

## Rollback Option

If you need to temporarily rollback to v1.x:

```yaml
- uses: rfernandezdo/inventariographdrawio@v2
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
```

However, we recommend migrating to v2.0 for better security.

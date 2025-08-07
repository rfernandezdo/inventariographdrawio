# Changelog

All notable changes to Azure Infrastructure Diagrams for Draw.io will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-08

### 🔄 BREAKING CHANGES

#### Migration to Azure Login v2 with OIDC
- **Removed**: `azure-credentials` input parameter
- **Added**: Dependency on `azure/login@v2` action for authentication
- **Security**: Migrated from service principal secrets to OIDC (OpenID Connect) authentication
- **Updated**: All documentation, examples, and workflows to use new authentication method

#### Migration Steps
1. Remove `azure-credentials` input from your workflows
2. Add `azure/login@v2` step before using this action
3. Configure OIDC secrets: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`
4. Add required permissions: `id-token: write` to your workflow

### Added
- **Enhanced Security**: OIDC authentication eliminates need for long-lived secrets
- **Better Error Handling**: Clearer error messages for authentication issues
- **Updated Azure CLI**: Upgraded to latest version for better compatibility

### Changed
- **Documentation**: Complete overhaul of setup guides and examples
- **Workflow Examples**: All example workflows updated to new authentication pattern
- **Action Schema**: Simplified input parameters

### Fixed
- **Azure CLI Version**: Updated to use latest stable Azure CLI version
- **Compatibility**: Better support for modern Azure environments

## [1.0.0] - 2025-01-XX

### Added - GitHub Action Release 🚀

#### Core Features
- **GitHub Action Support**: Complete integration as a GitHub Action for CI/CD workflows
- **Multiple Diagram Modes**: Infrastructure, Components, Network, and All-in-one multi-page diagrams
- **Multi-Tenant Support**: Filter by specific tenant or include all tenants
- **Automated Workflows**: Built-in examples for weekly reports, change detection, and multi-environment diagrams

#### Diagram Generation
- **Infrastructure Mode**: Complete hierarchical structure with DFS tree algorithm
- **Components Mode**: Grouped by service type and function for architecture analysis  
- **Network Mode**: Network topology with multi-subnet support for NSGs and Route Tables
- **All Mode**: Multi-page diagrams with all views in a single file

#### Automation Features
- **Flexible Commit Options**: None, direct push, or pull request creation
- **Advanced Filtering**: Include/exclude specific resources, subscriptions, or management groups
- **JSON Export**: Raw data export for custom analysis and processing
- **Performance Optimized**: Handles 1000+ resources efficiently

#### GitHub Integration
- **Pull Request Creation**: Automatic PRs with diagram updates and metadata
- **Branch Management**: Configurable target branches for different workflows
- **Output Metadata**: Resource counts, tenant information, and file paths
- **Error Handling**: Comprehensive error messages and troubleshooting guidance

#### Security & Compliance
- **Minimal Permissions**: Only requires Reader role on Azure subscriptions
- **No External Dependencies**: Runs entirely within GitHub Actions environment
- **Data Privacy**: No data sent to external services, stays in your repository
- **Service Principal**: Secure authentication using Azure service principals

### Technical Improvements

#### Performance & Scalability
- **High Performance**: Processes 1000+ resources in under 2 seconds (1,018 items/second)
- **Efficient Caching**: Local caching system for improved performance in repeated runs
- **Memory Optimized**: Handles large infrastructures without memory issues
- **Parallel Processing**: Optimized Azure API calls for faster data collection

#### Layout & Visualization
- **Advanced DFS Algorithm**: True tree structure using depth-first search
- **Smart Positioning**: Automatic centering and balanced layout
- **Multi-Subnet Support**: NSGs and Route Tables appear in both original location and subnet assignments
- **Hierarchical Filtering**: Option to show only functional dependencies (~21 vs ~100 edges)
- **Official Azure Icons**: Complete library of Azure service icons

#### Developer Experience
- **Comprehensive Documentation**: Complete setup guides and examples
- **Multiple Usage Modes**: GitHub Action, CLI local, and Python module
- **Extensive Examples**: 15+ workflow examples for different scenarios
- **Error Diagnostics**: Detailed error messages and troubleshooting guides
- **Template Workflows**: Ready-to-use workflow templates

### Documentation
- **ACTION_README.md**: Complete GitHub Action documentation
- **SETUP_GITHUB_ACTION.md**: Step-by-step setup guide
- **EXAMPLES.md**: Comprehensive examples for different use cases
- **Updated Documentation**: All existing docs updated for GitHub Action support

### Workflow Examples
- **Weekly Infrastructure Reports**: Automated weekly diagram generation with PRs
- **Infrastructure Change Detection**: Continuous monitoring with issue creation
- **Multi-Tenant Diagrams**: Separate diagrams for different tenants/environments
- **Network Security Analysis**: Focused network topology and security analysis
- **Manual Generation**: On-demand diagram generation with parameters

### Compatibility
- **Backward Compatibility**: All existing CLI functionality preserved
- **Cross-Platform**: Works on ubuntu-latest GitHub runners
- **Azure CLI Integration**: Seamless integration with Azure CLI and Resource Graph
- **Draw.io Compatibility**: Generated files work perfectly with draw.io/diagrams.net

### Known Limitations
- **Azure Permissions**: Requires Reader role on target subscriptions/management groups
- **Large Infrastructures**: Very large environments (5000+ resources) may hit GitHub Action timeouts
- **Complex Networks**: Extremely complex network topologies may require manual layout adjustment

---

## Previous Versions (CLI Only)

### [0.9.x] - 2024-2025
- CLI-only versions with core functionality
- Infrastructure, Components, and Network modes
- Multi-tenant support
- Performance optimizations
- Comprehensive testing suite

### [0.8.x] - 2024
- Initial public release
- Basic diagram generation
- Azure Resource Graph integration
- Draw.io export functionality

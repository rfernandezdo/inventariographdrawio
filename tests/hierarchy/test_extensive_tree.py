#!/usr/bin/env python3
"""
Test extensivo para verificar el algoritmo DFS con una amplia variedad de recursos de Azure
Simula un entorno empresarial real con múltiples suscripciones, tipos de recursos y dependencias complejas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from drawio_export import generate_drawio_file

def test_extensive_azure_tree():
    """Test del algoritmo DFS con recursos extensivos y múltiples tipos de Azure"""
    
    # Datos de prueba con estructura empresarial completa
    test_items = [
        # === NIVEL 0: MANAGEMENT GROUPS (jerarquía compleja) ===
        {
            'id': '/providers/Microsoft.Management/managementGroups/contoso-tenant',
            'name': 'Contoso Tenant Root',
            'type': 'Microsoft.Management/managementGroups'
        },
        {
            'id': '/providers/Microsoft.Management/managementGroups/contoso-platform',
            'name': 'Platform Services',
            'type': 'Microsoft.Management/managementGroups'
        },
        {
            'id': '/providers/Microsoft.Management/managementGroups/contoso-workloads',
            'name': 'Application Workloads',
            'type': 'Microsoft.Management/managementGroups'
        },
        {
            'id': '/providers/Microsoft.Management/managementGroups/contoso-sandbox',
            'name': 'Sandbox Environment',
            'type': 'Microsoft.Management/managementGroups'
        },
        
        # === NIVEL 1: SUSCRIPCIONES ===
        {
            'id': '/subscriptions/sub-platform-shared',
            'name': 'Platform Shared Services',
            'type': 'Microsoft.Resources/subscriptions'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce',
            'name': 'Production E-Commerce',
            'type': 'Microsoft.Resources/subscriptions'
        },
        {
            'id': '/subscriptions/sub-prod-erp',
            'name': 'Production ERP',
            'type': 'Microsoft.Resources/subscriptions'
        },
        {
            'id': '/subscriptions/sub-dev-general',
            'name': 'Development Environment',
            'type': 'Microsoft.Resources/subscriptions'
        },
        
        # === NIVEL 2: RESOURCE GROUPS ===
        
        # Platform Shared Services RGs
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network',
            'name': 'rg-shared-network',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-security',
            'name': 'rg-shared-security',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-monitoring',
            'name': 'rg-shared-monitoring',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        
        # E-Commerce Production RGs
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend',
            'name': 'rg-ecom-frontend',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend',
            'name': 'rg-ecom-backend',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data',
            'name': 'rg-ecom-data',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        
        # ERP Production RGs
        {
            'id': '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app',
            'name': 'rg-erp-app',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-database',
            'name': 'rg-erp-database',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        
        # Development RGs
        {
            'id': '/subscriptions/sub-dev-general/resourceGroups/rg-dev-apps',
            'name': 'rg-dev-apps',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        
        # === NIVEL 3: RECURSOS DE RED ===
        
        # Hub VNet (Platform)
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub',
            'name': 'vnet-hub',
            'type': 'Microsoft.Network/virtualNetworks'
        },
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-gateway',
            'name': 'GatewaySubnet',
            'type': 'Microsoft.Network/virtualNetworks/subnets'
        },
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-firewall',
            'name': 'AzureFirewallSubnet',
            'type': 'Microsoft.Network/virtualNetworks/subnets'
        },
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-shared',
            'name': 'subnet-shared-services',
            'type': 'Microsoft.Network/virtualNetworks/subnets'
        },
        
        # E-Commerce VNet
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/virtualNetworks/vnet-ecom',
            'name': 'vnet-ecommerce',
            'type': 'Microsoft.Network/virtualNetworks'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/virtualNetworks/vnet-ecom/subnets/subnet-web',
            'name': 'subnet-web-tier',
            'type': 'Microsoft.Network/virtualNetworks/subnets'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Network/virtualNetworks/vnet-ecom/subnets/subnet-api',
            'name': 'subnet-api-tier',
            'type': 'Microsoft.Network/virtualNetworks/subnets'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Network/virtualNetworks/vnet-ecom/subnets/subnet-data',
            'name': 'subnet-data-tier',
            'type': 'Microsoft.Network/virtualNetworks/subnets'
        },
        
        # === RECURSOS DE GATEWAY Y SEGURIDAD ===
        
        # VPN Gateway
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworkGateways/vpn-gateway',
            'name': 'vpn-gateway-main',
            'type': 'Microsoft.Network/virtualNetworkGateways'
        },
        
        # Azure Firewall
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-security/providers/Microsoft.Network/azureFirewalls/fw-hub',
            'name': 'fw-hub-main',
            'type': 'Microsoft.Network/azureFirewalls'
        },
        
        # Application Gateway
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/applicationGateways/agw-ecom',
            'name': 'agw-ecommerce',
            'type': 'Microsoft.Network/applicationGateways'
        },
        
        # Load Balancer
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Network/loadBalancers/lb-api',
            'name': 'lb-api-internal',
            'type': 'Microsoft.Network/loadBalancers'
        },
        
        # Network Security Groups
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/networkSecurityGroups/nsg-web',
            'name': 'nsg-web-tier',
            'type': 'Microsoft.Network/networkSecurityGroups'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Network/networkSecurityGroups/nsg-api',
            'name': 'nsg-api-tier',
            'type': 'Microsoft.Network/networkSecurityGroups'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Network/networkSecurityGroups/nsg-data',
            'name': 'nsg-data-tier',
            'type': 'Microsoft.Network/networkSecurityGroups'
        },
        
        # === RECURSOS DE COMPUTE ===
        
        # Virtual Machine Scale Sets
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Compute/virtualMachineScaleSets/vmss-web',
            'name': 'vmss-web-frontend',
            'type': 'Microsoft.Compute/virtualMachineScaleSets'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Compute/virtualMachineScaleSets/vmss-api',
            'name': 'vmss-api-backend',
            'type': 'Microsoft.Compute/virtualMachineScaleSets'
        },
        
        # Virtual Machines
        {
            'id': '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/virtualMachines/vm-erp-app01',
            'name': 'vm-erp-app01',
            'type': 'Microsoft.Compute/virtualMachines'
        },
        {
            'id': '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/virtualMachines/vm-erp-app02',
            'name': 'vm-erp-app02',
            'type': 'Microsoft.Compute/virtualMachines'
        },
        
        # Disks
        {
            'id': '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/disks/vm-erp-app01-osdisk',
            'name': 'vm-erp-app01-osdisk',
            'type': 'Microsoft.Compute/disks'
        },
        {
            'id': '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/disks/vm-erp-app01-datadisk',
            'name': 'vm-erp-app01-datadisk',
            'type': 'Microsoft.Compute/disks'
        },
        {
            'id': '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/disks/vm-erp-app02-osdisk',
            'name': 'vm-erp-app02-osdisk',
            'type': 'Microsoft.Compute/disks'
        },
        
        # Network Interfaces
        {
            'id': '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Network/networkInterfaces/vm-erp-app01-nic',
            'name': 'vm-erp-app01-nic',
            'type': 'Microsoft.Network/networkInterfaces'
        },
        {
            'id': '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Network/networkInterfaces/vm-erp-app02-nic',
            'name': 'vm-erp-app02-nic',
            'type': 'Microsoft.Network/networkInterfaces'
        },
        
        # === RECURSOS DE BASE DE DATOS ===
        
        # Azure SQL
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Sql/servers/sql-ecom-prod',
            'name': 'sql-ecom-prod',
            'type': 'Microsoft.Sql/servers'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Sql/servers/sql-ecom-prod/databases/db-ecommerce',
            'name': 'db-ecommerce-main',
            'type': 'Microsoft.Sql/servers/databases'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Sql/servers/sql-ecom-prod/databases/db-analytics',
            'name': 'db-ecommerce-analytics',
            'type': 'Microsoft.Sql/servers/databases'
        },
        
        # Azure Database for PostgreSQL
        {
            'id': '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-database/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-erp-prod',
            'name': 'psql-erp-prod',
            'type': 'Microsoft.DBforPostgreSQL/flexibleServers'
        },
        
        # CosmosDB
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-ecom-sessions',
            'name': 'cosmos-ecom-sessions',
            'type': 'Microsoft.DocumentDB/databaseAccounts'
        },
        
        # === RECURSOS DE STORAGE ===
        
        # Storage Accounts
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Storage/storageAccounts/stecomprod001',
            'name': 'stecomprod001',
            'type': 'Microsoft.Storage/storageAccounts'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Storage/storageAccounts/stecomstatic001',
            'name': 'stecomstatic001',
            'type': 'Microsoft.Storage/storageAccounts'
        },
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-monitoring/providers/Microsoft.Storage/storageAccounts/stsharedlogs001',
            'name': 'stsharedlogs001',
            'type': 'Microsoft.Storage/storageAccounts'
        },
        
        # === RECURSOS DE APLICACIÓN ===
        
        # App Services
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Web/serverfarms/asp-ecom-api',
            'name': 'asp-ecom-api',
            'type': 'Microsoft.Web/serverfarms'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Web/sites/app-ecom-api',
            'name': 'app-ecom-api',
            'type': 'Microsoft.Web/sites'
        },
        {
            'id': '/subscriptions/sub-dev-general/resourceGroups/rg-dev-apps/providers/Microsoft.Web/sites/app-dev-prototype',
            'name': 'app-dev-prototype',
            'type': 'Microsoft.Web/sites'
        },
        
        # Function Apps
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Web/sites/func-ecom-processing',
            'name': 'func-ecom-processing',
            'type': 'Microsoft.Web/sites',
            'kind': 'functionapp'
        },
        
        # === RECURSOS DE SEGURIDAD ===
        
        # Key Vaults
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-security/providers/Microsoft.KeyVault/vaults/kv-shared-secrets',
            'name': 'kv-shared-secrets',
            'type': 'Microsoft.KeyVault/vaults'
        },
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.KeyVault/vaults/kv-ecom-prod',
            'name': 'kv-ecom-prod',
            'type': 'Microsoft.KeyVault/vaults'
        },
        
        # === RECURSOS DE MONITOREO ===
        
        # Log Analytics Workspace
        {
            'id': '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-monitoring/providers/Microsoft.OperationalInsights/workspaces/law-central-logs',
            'name': 'law-central-logs',
            'type': 'Microsoft.OperationalInsights/workspaces'
        },
        
        # Application Insights
        {
            'id': '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Insights/components/appi-ecom-api',
            'name': 'appi-ecom-api',
            'type': 'Microsoft.Insights/components'
        }
    ]
    
    # Dependencias complejas (jerárquicas y de relación)
    test_dependencies = [
        # === DEPENDENCIAS JERÁRQUICAS (para el árbol DFS) ===
        
        # Management Groups jerarquía
        ('/providers/Microsoft.Management/managementGroups/contoso-platform', 
         '/providers/Microsoft.Management/managementGroups/contoso-tenant'),
        ('/providers/Microsoft.Management/managementGroups/contoso-workloads', 
         '/providers/Microsoft.Management/managementGroups/contoso-tenant'),
        ('/providers/Microsoft.Management/managementGroups/contoso-sandbox', 
         '/providers/Microsoft.Management/managementGroups/contoso-tenant'),
        
        # Suscripciones → Management Groups
        ('/subscriptions/sub-platform-shared', '/providers/Microsoft.Management/managementGroups/contoso-platform'),
        ('/subscriptions/sub-prod-ecommerce', '/providers/Microsoft.Management/managementGroups/contoso-workloads'),
        ('/subscriptions/sub-prod-erp', '/providers/Microsoft.Management/managementGroups/contoso-workloads'),
        ('/subscriptions/sub-dev-general', '/providers/Microsoft.Management/managementGroups/contoso-sandbox'),
        
        # Resource Groups → Suscripciones
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network', '/subscriptions/sub-platform-shared'),
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-security', '/subscriptions/sub-platform-shared'),
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-monitoring', '/subscriptions/sub-platform-shared'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend', '/subscriptions/sub-prod-ecommerce'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend', '/subscriptions/sub-prod-ecommerce'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data', '/subscriptions/sub-prod-ecommerce'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app', '/subscriptions/sub-prod-erp'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-database', '/subscriptions/sub-prod-erp'),
        ('/subscriptions/sub-dev-general/resourceGroups/rg-dev-apps', '/subscriptions/sub-dev-general'),
        
        # Recursos → Resource Groups (muestreo de los principales)
        # Platform resources
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub',
         '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network'),
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworkGateways/vpn-gateway',
         '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network'),
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-security/providers/Microsoft.Network/azureFirewalls/fw-hub',
         '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-security'),
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-security/providers/Microsoft.KeyVault/vaults/kv-shared-secrets',
         '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-security'),
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-monitoring/providers/Microsoft.OperationalInsights/workspaces/law-central-logs',
         '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-monitoring'),
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-monitoring/providers/Microsoft.Storage/storageAccounts/stsharedlogs001',
         '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-monitoring'),
        
        # E-commerce resources
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/virtualNetworks/vnet-ecom',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/applicationGateways/agw-ecom',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Compute/virtualMachineScaleSets/vmss-web',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Storage/storageAccounts/stecomstatic001',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Compute/virtualMachineScaleSets/vmss-api',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Network/loadBalancers/lb-api',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Web/serverfarms/asp-ecom-api',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Web/sites/app-ecom-api',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Web/sites/func-ecom-processing',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.KeyVault/vaults/kv-ecom-prod',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Insights/components/appi-ecom-api',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Sql/servers/sql-ecom-prod',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-ecom-sessions',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Storage/storageAccounts/stecomprod001',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data'),
        
        # ERP resources
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/virtualMachines/vm-erp-app01',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/virtualMachines/vm-erp-app02',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/disks/vm-erp-app01-osdisk',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/disks/vm-erp-app01-datadisk',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/disks/vm-erp-app02-osdisk',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Network/networkInterfaces/vm-erp-app01-nic',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Network/networkInterfaces/vm-erp-app02-nic',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-database/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-erp-prod',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-database'),
        
        # Dev resources
        ('/subscriptions/sub-dev-general/resourceGroups/rg-dev-apps/providers/Microsoft.Web/sites/app-dev-prototype',
         '/subscriptions/sub-dev-general/resourceGroups/rg-dev-apps'),
        
        # === DEPENDENCIAS DE RELACIÓN (líneas punteadas) ===
        
        # Subnets → VNets
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-gateway',
         '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub'),
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-firewall',
         '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub'),
        ('/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub/subnets/subnet-shared',
         '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/virtualNetworks/vnet-ecom/subnets/subnet-web',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/virtualNetworks/vnet-ecom'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Network/virtualNetworks/vnet-ecom/subnets/subnet-api',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/virtualNetworks/vnet-ecom'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Network/virtualNetworks/vnet-ecom/subnets/subnet-data',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/virtualNetworks/vnet-ecom'),
        
        # SQL Database → SQL Server
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Sql/servers/sql-ecom-prod/databases/db-ecommerce',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Sql/servers/sql-ecom-prod'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Sql/servers/sql-ecom-prod/databases/db-analytics',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Sql/servers/sql-ecom-prod'),
        
        # App Service → App Service Plan
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Web/sites/app-ecom-api',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Web/serverfarms/asp-ecom-api'),
        
        # VM → Disk dependencies
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/disks/vm-erp-app01-osdisk',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/virtualMachines/vm-erp-app01'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/disks/vm-erp-app01-datadisk',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/virtualMachines/vm-erp-app01'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/disks/vm-erp-app02-osdisk',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/virtualMachines/vm-erp-app02'),
        
        # VM → NIC dependencies
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Network/networkInterfaces/vm-erp-app01-nic',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/virtualMachines/vm-erp-app01'),
        ('/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Network/networkInterfaces/vm-erp-app02-nic',
         '/subscriptions/sub-prod-erp/resourceGroups/rg-erp-app/providers/Microsoft.Compute/virtualMachines/vm-erp-app02'),
        
        # Security Group → Subnet associations
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/networkSecurityGroups/nsg-web',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/virtualNetworks/vnet-ecom/subnets/subnet-web'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Network/networkSecurityGroups/nsg-api',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Network/virtualNetworks/vnet-ecom/subnets/subnet-api'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Network/networkSecurityGroups/nsg-data',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Network/virtualNetworks/vnet-ecom/subnets/subnet-data'),
        
        # Application dependencies
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Web/sites/app-ecom-api',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Sql/servers/sql-ecom-prod'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Web/sites/app-ecom-api',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.KeyVault/vaults/kv-ecom-prod'),
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Web/sites/func-ecom-processing',
         '/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-data/providers/Microsoft.Storage/storageAccounts/stecomprod001'),
        
        # Cross-resource group networking
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-frontend/providers/Microsoft.Network/virtualNetworks/vnet-ecom',
         '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-network/providers/Microsoft.Network/virtualNetworks/vnet-hub'),
        
        # Monitoring dependencies
        ('/subscriptions/sub-prod-ecommerce/resourceGroups/rg-ecom-backend/providers/Microsoft.Insights/components/appi-ecom-api',
         '/subscriptions/sub-platform-shared/resourceGroups/rg-shared-monitoring/providers/Microsoft.OperationalInsights/workspaces/law-central-logs'),
    ]
    
    print("🧪 Probando algoritmo DFS con estructura Azure extensiva...")
    print(f"📊 Elementos: {len(test_items)} recursos")
    print(f"🔗 Dependencias: {len(test_dependencies)} relaciones")
    print(f"📈 Management Groups: 4 niveles")
    print(f"🎯 Suscripciones: 4 ambientes")
    print(f"📁 Resource Groups: 9 grupos")
    print(f"🌐 Tipos de recursos: >20 tipos diferentes")
    
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    # Verificaciones extensivas
    assert content is not None, "No se generó contenido"
    assert len(content) > 5000, "El contenido es demasiado corto para una estructura extensiva"
    
    # Verificar jerarquía de Management Groups
    assert 'Contoso Tenant Root' in content, "No se encontró el MG raíz"
    assert 'Platform Services' in content, "No se encontró el MG Platform"
    assert 'Application Workloads' in content, "No se encontró el MG Workloads"
    assert 'Sandbox Environment' in content, "No se encontró el MG Sandbox"
    
    # Verificar múltiples suscripciones
    assert 'Platform Shared Services' in content, "No se encontró sub platform"
    assert 'Production E-Commerce' in content, "No se encontró sub ecommerce"
    assert 'Production ERP' in content, "No se encontró sub ERP"
    assert 'Development Environment' in content, "No se encontró sub dev"
    
    # Verificar diversos tipos de recursos
    assert 'vnet-hub' in content, "No se encontró Hub VNet"
    assert 'vpn-gateway-main' in content, "No se encontró VPN Gateway"
    assert 'fw-hub-main' in content, "No se encontró Azure Firewall"
    assert 'agw-ecommerce' in content, "No se encontró Application Gateway"
    assert 'vmss-web-frontend' in content, "No se encontró VMSS Web"
    assert 'sql-ecom-prod' in content, "No se encontró SQL Server"
    assert 'cosmos-ecom-sessions' in content, "No se encontró CosmosDB"
    assert 'kv-shared-secrets' in content, "No se encontró Key Vault"
    assert 'law-central-logs' in content, "No se encontró Log Analytics"
    
    # Verificar tipos de líneas (sólidas jerárquicas y punteadas de relación)
    assert 'strokeColor=#1976d2;strokeWidth=2;' in content, "No se encontraron líneas jerárquicas"
    assert 'dashed=1;' in content, "No se encontraron líneas de relación"
    
    # Guardar archivo de prueba
    output_file = 'test-extensive-azure-tree.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test extensivo completado exitosamente")
    print(f"📁 Archivo generado: {output_file}")
    print(f"📏 Tamaño del contenido: {len(content)} caracteres")
    print(f"🎯 Resultado: Algoritmo DFS maneja estructura empresarial compleja correctamente")

def test_performance_metrics():
    """Test adicional para medir rendimiento del algoritmo"""
    
    import time
    start_time = time.time()
    
    # Ejecutar el test extensivo
    test_extensive_azure_tree()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\n📊 === MÉTRICAS DE RENDIMIENTO ===")
    print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos")
    print(f"📈 Rendimiento: {'EXCELENTE' if execution_time < 5 else 'BUENO' if execution_time < 10 else 'MEJORABLE'}")
    
    if execution_time > 10:
        print("⚠️  Tiempo elevado - considerar optimizaciones para estructuras muy grandes")
    else:
        print("✅ Rendimiento óptimo para estructuras empresariales")

if __name__ == "__main__":
    try:
        test_extensive_azure_tree()
        test_performance_metrics()
        print("\n🎉 TODOS LOS TESTS EXTENSIVOS PASARON CORRECTAMENTE")
    except Exception as e:
        print(f"\n❌ ERROR en test extensivo: {e}")
        raise

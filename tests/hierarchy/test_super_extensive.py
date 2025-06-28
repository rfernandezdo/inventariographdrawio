#!/usr/bin/env python3
"""
Test super extensivo para verificar casos edge, recursos especializados y escalabilidad del algoritmo DFS
Incluye recursos menos comunes, configuraciones complejas y casos límite
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from drawio_export import generate_drawio_file

def test_edge_cases_and_specialized_resources():
    """Test de casos edge y recursos especializados de Azure"""
    
    # Datos de prueba con recursos especializados y casos edge
    test_items = [
        # === MANAGEMENT GROUPS ANIDADOS (5 niveles) ===
        {
            'id': '/providers/Microsoft.Management/managementGroups/root-tenant',
            'name': 'Enterprise Root Tenant',
            'type': 'Microsoft.Management/managementGroups'
        },
        {
            'id': '/providers/Microsoft.Management/managementGroups/enterprise-divisions',
            'name': 'Enterprise Divisions',
            'type': 'Microsoft.Management/managementGroups'
        },
        {
            'id': '/providers/Microsoft.Management/managementGroups/north-america',
            'name': 'North America Region',
            'type': 'Microsoft.Management/managementGroups'
        },
        {
            'id': '/providers/Microsoft.Management/managementGroups/usa-operations',
            'name': 'USA Operations',
            'type': 'Microsoft.Management/managementGroups'
        },
        {
            'id': '/providers/Microsoft.Management/managementGroups/usa-prod-workloads',
            'name': 'USA Production Workloads',
            'type': 'Microsoft.Management/managementGroups'
        },
        
        # === SUSCRIPCIONES ESPECIALIZADAS ===
        {
            'id': '/subscriptions/sub-hub-connectivity',
            'name': 'Hub Connectivity Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        {
            'id': '/subscriptions/sub-shared-services',
            'name': 'Shared Services Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        {
            'id': '/subscriptions/sub-ai-ml-platform',
            'name': 'AI/ML Platform Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        {
            'id': '/subscriptions/sub-iot-telemetry',
            'name': 'IoT Telemetry Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        {
            'id': '/subscriptions/sub-disaster-recovery',
            'name': 'Disaster Recovery Subscription',
            'type': 'Microsoft.Resources/subscriptions'
        },
        
        # === RESOURCE GROUPS ESPECIALIZADOS ===
        {
            'id': '/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns',
            'name': 'rg-global-dns',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-hub-connectivity/resourceGroups/rg-express-route',
            'name': 'rg-express-route',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-shared-services/resourceGroups/rg-backup-vault',
            'name': 'rg-backup-vault',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning',
            'name': 'rg-machine-learning',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-cognitive-services',
            'name': 'rg-cognitive-services',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-iot-hub',
            'name': 'rg-iot-hub',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series',
            'name': 'rg-time-series',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'id': '/subscriptions/sub-disaster-recovery/resourceGroups/rg-site-recovery',
            'name': 'rg-site-recovery',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        
        # === RECURSOS DE RED AVANZADOS ===
        
        # ExpressRoute
        {
            'id': '/subscriptions/sub-hub-connectivity/resourceGroups/rg-express-route/providers/Microsoft.Network/expressRouteCircuits/er-primary',
            'name': 'er-primary-circuit',
            'type': 'Microsoft.Network/expressRouteCircuits'
        },
        {
            'id': '/subscriptions/sub-hub-connectivity/resourceGroups/rg-express-route/providers/Microsoft.Network/expressRouteGateways/ergw-hub',
            'name': 'ergw-hub-gateway',
            'type': 'Microsoft.Network/expressRouteGateways'
        },
        
        # Private DNS Zones
        {
            'id': '/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns/providers/Microsoft.Network/privateDnsZones/privatelink.database.windows.net',
            'name': 'privatelink.database.windows.net',
            'type': 'Microsoft.Network/privateDnsZones'
        },
        {
            'id': '/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns/providers/Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net',
            'name': 'privatelink.blob.core.windows.net',
            'type': 'Microsoft.Network/privateDnsZones'
        },
        
        # Traffic Manager
        {
            'id': '/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns/providers/Microsoft.Network/trafficManagerProfiles/tm-global-lb',
            'name': 'tm-global-loadbalancer',
            'type': 'Microsoft.Network/trafficManagerProfiles'
        },
        
        # Azure Front Door
        {
            'id': '/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns/providers/Microsoft.Network/frontDoors/fd-global-cdn',
            'name': 'fd-global-cdn',
            'type': 'Microsoft.Network/frontDoors'
        },
        
        # === RECURSOS DE AI/ML ===
        
        # Machine Learning Workspace
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.MachineLearningServices/workspaces/mlw-prod',
            'name': 'mlw-production',
            'type': 'Microsoft.MachineLearningServices/workspaces'
        },
        
        # Cognitive Services
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-cognitive-services/providers/Microsoft.CognitiveServices/accounts/cog-text-analytics',
            'name': 'cog-text-analytics',
            'type': 'Microsoft.CognitiveServices/accounts'
        },
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-cognitive-services/providers/Microsoft.CognitiveServices/accounts/cog-computer-vision',
            'name': 'cog-computer-vision',
            'type': 'Microsoft.CognitiveServices/accounts'
        },
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-cognitive-services/providers/Microsoft.CognitiveServices/accounts/cog-speech-services',
            'name': 'cog-speech-services',
            'type': 'Microsoft.CognitiveServices/accounts'
        },
        
        # Azure Databricks
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.Databricks/workspaces/dbw-analytics',
            'name': 'dbw-analytics-platform',
            'type': 'Microsoft.Databricks/workspaces'
        },
        
        # === RECURSOS DE IoT ===
        
        # IoT Hub
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-iot-hub/providers/Microsoft.Devices/IoTHubs/iothub-telemetry',
            'name': 'iothub-telemetry-prod',
            'type': 'Microsoft.Devices/IoTHubs'
        },
        
        # IoT Central
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-iot-hub/providers/Microsoft.IoTCentral/IoTApps/iotc-fleet-mgmt',
            'name': 'iotc-fleet-management',
            'type': 'Microsoft.IoTCentral/IoTApps'
        },
        
        # Time Series Insights
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.TimeSeriesInsights/environments/tsi-telemetry',
            'name': 'tsi-telemetry-analytics',
            'type': 'Microsoft.TimeSeriesInsights/environments'
        },
        
        # Event Hubs
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.EventHub/namespaces/evhns-telemetry',
            'name': 'evhns-telemetry-stream',
            'type': 'Microsoft.EventHub/namespaces'
        },
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.EventHub/namespaces/evhns-telemetry/eventhubs/evh-device-data',
            'name': 'evh-device-data',
            'type': 'Microsoft.EventHub/namespaces/eventhubs'
        },
        
        # Stream Analytics
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.StreamAnalytics/streamingjobs/asa-realtime',
            'name': 'asa-realtime-processing',
            'type': 'Microsoft.StreamAnalytics/streamingjobs'
        },
        
        # === RECURSOS DE BACKUP Y DR ===
        
        # Recovery Services Vault
        {
            'id': '/subscriptions/sub-shared-services/resourceGroups/rg-backup-vault/providers/Microsoft.RecoveryServices/vaults/rsv-central-backup',
            'name': 'rsv-central-backup',
            'type': 'Microsoft.RecoveryServices/vaults'
        },
        
        # Site Recovery
        {
            'id': '/subscriptions/sub-disaster-recovery/resourceGroups/rg-site-recovery/providers/Microsoft.RecoveryServices/vaults/rsv-site-recovery',
            'name': 'rsv-site-recovery',
            'type': 'Microsoft.RecoveryServices/vaults'
        },
        
        # === RECURSOS DE CONTAINER Y MICROSERVICIOS ===
        
        # Azure Kubernetes Service
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.ContainerService/managedClusters/aks-ml-compute',
            'name': 'aks-ml-compute',
            'type': 'Microsoft.ContainerService/managedClusters'
        },
        
        # Container Registry
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.ContainerRegistry/registries/acrmlopsprod',
            'name': 'acrmlopsprod',
            'type': 'Microsoft.ContainerRegistry/registries'
        },
        
        # Container Instances
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.ContainerInstance/containerGroups/aci-data-processor',
            'name': 'aci-data-processor',
            'type': 'Microsoft.ContainerInstance/containerGroups'
        },
        
        # === RECURSOS DE INTEGRACIÓN ===
        
        # Logic Apps
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.Logic/workflows/logic-alert-processor',
            'name': 'logic-alert-processor',
            'type': 'Microsoft.Logic/workflows'
        },
        
        # API Management
        {
            'id': '/subscriptions/sub-shared-services/resourceGroups/rg-backup-vault/providers/Microsoft.ApiManagement/service/apim-enterprise-gateway',
            'name': 'apim-enterprise-gateway',
            'type': 'Microsoft.ApiManagement/service'
        },
        
        # Service Bus
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.ServiceBus/namespaces/sb-messaging',
            'name': 'sb-messaging-hub',
            'type': 'Microsoft.ServiceBus/namespaces'
        },
        
        # === RECURSOS DE DATOS AVANZADOS ===
        
        # Azure Synapse Analytics
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.Synapse/workspaces/synw-analytics',
            'name': 'synw-analytics-platform',
            'type': 'Microsoft.Synapse/workspaces'
        },
        
        # Data Factory
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.DataFactory/factories/adf-ml-pipeline',
            'name': 'adf-ml-pipeline',
            'type': 'Microsoft.DataFactory/factories'
        },
        
        # Data Lake Storage
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.Storage/storageAccounts/datalakemlprod',
            'name': 'datalakemlprod',
            'type': 'Microsoft.Storage/storageAccounts',
            'kind': 'StorageV2',
            'properties': {'isHnsEnabled': True}
        },
        
        # Azure Purview
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.Purview/accounts/purview-data-catalog',
            'name': 'purview-data-catalog',
            'type': 'Microsoft.Purview/accounts'
        },
        
        # === RECURSOS DE SEGURIDAD AVANZADOS ===
        
        # Azure Sentinel
        {
            'id': '/subscriptions/sub-shared-services/resourceGroups/rg-backup-vault/providers/Microsoft.SecurityInsights/solutions/sentinel-siem',
            'name': 'sentinel-siem-solution',
            'type': 'Microsoft.SecurityInsights/solutions'
        },
        
        # Azure Defender
        {
            'id': '/subscriptions/sub-shared-services/resourceGroups/rg-backup-vault/providers/Microsoft.Security/pricings/defender-servers',
            'name': 'defender-for-servers',
            'type': 'Microsoft.Security/pricings'
        },
        
        # Azure Bastion
        {
            'id': '/subscriptions/sub-hub-connectivity/resourceGroups/rg-express-route/providers/Microsoft.Network/bastionHosts/bastion-hub',
            'name': 'bastion-hub-jump',
            'type': 'Microsoft.Network/bastionHosts'
        },
        
        # === RECURSOS POCO COMUNES ===
        
        # Azure Digital Twins
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-iot-hub/providers/Microsoft.DigitalTwins/digitalTwinsInstances/dt-smart-building',
            'name': 'dt-smart-building',
            'type': 'Microsoft.DigitalTwins/digitalTwinsInstances'
        },
        
        # Azure Maps
        {
            'id': '/subscriptions/sub-iot-telemetry/resourceGroups/rg-iot-hub/providers/Microsoft.Maps/accounts/maps-fleet-tracking',
            'name': 'maps-fleet-tracking',
            'type': 'Microsoft.Maps/accounts'
        },
        
        # Azure Batch
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.Batch/batchAccounts/batch-ml-training',
            'name': 'batch-ml-training',
            'type': 'Microsoft.Batch/batchAccounts'
        },
        
        # Azure HPC Cache
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.StorageCache/caches/hpc-ml-cache',
            'name': 'hpc-ml-cache',
            'type': 'Microsoft.StorageCache/caches'
        },
        
        # Azure NetApp Files
        {
            'id': '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.NetApp/netAppAccounts/anf-high-perf',
            'name': 'anf-high-performance',
            'type': 'Microsoft.NetApp/netAppAccounts'
        }
    ]
    
    # Dependencias complejas con casos edge
    test_dependencies = [
        # === DEPENDENCIAS JERÁRQUICAS (5 niveles de MG) ===
        ('/providers/Microsoft.Management/managementGroups/enterprise-divisions', 
         '/providers/Microsoft.Management/managementGroups/root-tenant'),
        ('/providers/Microsoft.Management/managementGroups/north-america', 
         '/providers/Microsoft.Management/managementGroups/enterprise-divisions'),
        ('/providers/Microsoft.Management/managementGroups/usa-operations', 
         '/providers/Microsoft.Management/managementGroups/north-america'),
        ('/providers/Microsoft.Management/managementGroups/usa-prod-workloads', 
         '/providers/Microsoft.Management/managementGroups/usa-operations'),
        
        # Suscripciones → Management Groups
        ('/subscriptions/sub-hub-connectivity', '/providers/Microsoft.Management/managementGroups/usa-operations'),
        ('/subscriptions/sub-shared-services', '/providers/Microsoft.Management/managementGroups/usa-operations'),
        ('/subscriptions/sub-ai-ml-platform', '/providers/Microsoft.Management/managementGroups/usa-prod-workloads'),
        ('/subscriptions/sub-iot-telemetry', '/providers/Microsoft.Management/managementGroups/usa-prod-workloads'),
        ('/subscriptions/sub-disaster-recovery', '/providers/Microsoft.Management/managementGroups/usa-operations'),
        
        # Resource Groups → Suscripciones
        ('/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns', '/subscriptions/sub-hub-connectivity'),
        ('/subscriptions/sub-hub-connectivity/resourceGroups/rg-express-route', '/subscriptions/sub-hub-connectivity'),
        ('/subscriptions/sub-shared-services/resourceGroups/rg-backup-vault', '/subscriptions/sub-shared-services'),
        ('/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning', '/subscriptions/sub-ai-ml-platform'),
        ('/subscriptions/sub-ai-ml-platform/resourceGroups/rg-cognitive-services', '/subscriptions/sub-ai-ml-platform'),
        ('/subscriptions/sub-iot-telemetry/resourceGroups/rg-iot-hub', '/subscriptions/sub-iot-telemetry'),
        ('/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series', '/subscriptions/sub-iot-telemetry'),
        ('/subscriptions/sub-disaster-recovery/resourceGroups/rg-site-recovery', '/subscriptions/sub-disaster-recovery'),
        
        # Recursos especializados → Resource Groups (muestreo)
        ('/subscriptions/sub-hub-connectivity/resourceGroups/rg-express-route/providers/Microsoft.Network/expressRouteCircuits/er-primary',
         '/subscriptions/sub-hub-connectivity/resourceGroups/rg-express-route'),
        ('/subscriptions/sub-hub-connectivity/resourceGroups/rg-express-route/providers/Microsoft.Network/expressRouteGateways/ergw-hub',
         '/subscriptions/sub-hub-connectivity/resourceGroups/rg-express-route'),
        ('/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns/providers/Microsoft.Network/privateDnsZones/privatelink.database.windows.net',
         '/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns'),
        ('/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns/providers/Microsoft.Network/trafficManagerProfiles/tm-global-lb',
         '/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns'),
        ('/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns/providers/Microsoft.Network/frontDoors/fd-global-cdn',
         '/subscriptions/sub-hub-connectivity/resourceGroups/rg-global-dns'),
        ('/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.MachineLearningServices/workspaces/mlw-prod',
         '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning'),
        ('/subscriptions/sub-ai-ml-platform/resourceGroups/rg-cognitive-services/providers/Microsoft.CognitiveServices/accounts/cog-text-analytics',
         '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-cognitive-services'),
        ('/subscriptions/sub-iot-telemetry/resourceGroups/rg-iot-hub/providers/Microsoft.Devices/IoTHubs/iothub-telemetry',
         '/subscriptions/sub-iot-telemetry/resourceGroups/rg-iot-hub'),
        ('/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.EventHub/namespaces/evhns-telemetry',
         '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series'),
        ('/subscriptions/sub-shared-services/resourceGroups/rg-backup-vault/providers/Microsoft.RecoveryServices/vaults/rsv-central-backup',
         '/subscriptions/sub-shared-services/resourceGroups/rg-backup-vault'),
        
        # === DEPENDENCIAS DE RELACIÓN (especializadas) ===
        
        # Event Hub → Event Hub Namespace
        ('/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.EventHub/namespaces/evhns-telemetry/eventhubs/evh-device-data',
         '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.EventHub/namespaces/evhns-telemetry'),
        
        # IoT Hub → Event Hub (telemetría)
        ('/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.EventHub/namespaces/evhns-telemetry',
         '/subscriptions/sub-iot-telemetry/resourceGroups/rg-iot-hub/providers/Microsoft.Devices/IoTHubs/iothub-telemetry'),
        
        # Stream Analytics → Event Hub (input)
        ('/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.StreamAnalytics/streamingjobs/asa-realtime',
         '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.EventHub/namespaces/evhns-telemetry/eventhubs/evh-device-data'),
        
        # Time Series Insights → Event Hub
        ('/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.TimeSeriesInsights/environments/tsi-telemetry',
         '/subscriptions/sub-iot-telemetry/resourceGroups/rg-time-series/providers/Microsoft.EventHub/namespaces/evhns-telemetry'),
        
        # ML Workspace → Data Lake
        ('/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.MachineLearningServices/workspaces/mlw-prod',
         '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.Storage/storageAccounts/datalakemlprod'),
        
        # AKS → Container Registry
        ('/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.ContainerService/managedClusters/aks-ml-compute',
         '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.ContainerRegistry/registries/acrmlopsprod'),
        
        # Databricks → Data Lake
        ('/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.Databricks/workspaces/dbw-analytics',
         '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.Storage/storageAccounts/datalakemlprod'),
        
        # Data Factory → Synapse
        ('/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.DataFactory/factories/adf-ml-pipeline',
         '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.Synapse/workspaces/synw-analytics'),
        
        # Digital Twins → IoT Hub
        ('/subscriptions/sub-iot-telemetry/resourceGroups/rg-iot-hub/providers/Microsoft.DigitalTwins/digitalTwinsInstances/dt-smart-building',
         '/subscriptions/sub-iot-telemetry/resourceGroups/rg-iot-hub/providers/Microsoft.Devices/IoTHubs/iothub-telemetry'),
        
        # Purview → Data Lake (catalogación)
        ('/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.Purview/accounts/purview-data-catalog',
         '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-machine-learning/providers/Microsoft.Storage/storageAccounts/datalakemlprod'),
        
        # API Management → múltiples servicios (ejemplo cross-subscription)
        ('/subscriptions/sub-shared-services/resourceGroups/rg-backup-vault/providers/Microsoft.ApiManagement/service/apim-enterprise-gateway',
         '/subscriptions/sub-ai-ml-platform/resourceGroups/rg-cognitive-services/providers/Microsoft.CognitiveServices/accounts/cog-text-analytics')
    ]
    
    print("🧪 Probando casos edge y recursos especializados de Azure...")
    print(f"📊 Elementos: {len(test_items)} recursos especializados")
    print(f"🔗 Dependencias: {len(test_dependencies)} relaciones complejas")
    print(f"🏗️  Management Groups: 5 niveles anidados")
    print(f"🚀 Tipos de recursos: IoT, AI/ML, Data Analytics, Networking avanzado, etc.")
    
    content = generate_drawio_file(
        test_items, 
        test_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    # Verificaciones de casos edge
    assert content is not None, "No se generó contenido"
    assert len(content) > 3000, "El contenido es demasiado corto para recursos especializados"
    
    # Verificar jerarquía profunda de Management Groups
    assert 'Enterprise Root Tenant' in content, "No se encontró MG nivel 0"
    assert 'Enterprise Divisions' in content, "No se encontró MG nivel 1"
    assert 'North America Region' in content, "No se encontró MG nivel 2"
    assert 'USA Operations' in content, "No se encontró MG nivel 3"
    assert 'USA Production Workloads' in content, "No se encontró MG nivel 4"
    
    # Verificar recursos especializados de AI/ML
    assert 'mlw-production' in content, "No se encontró ML Workspace"
    assert 'cog-text-analytics' in content, "No se encontró Cognitive Services"
    assert 'dbw-analytics-platform' in content, "No se encontró Databricks"
    assert 'synw-analytics-platform' in content, "No se encontró Synapse"
    
    # Verificar recursos de IoT
    assert 'iothub-telemetry-prod' in content, "No se encontró IoT Hub"
    assert 'tsi-telemetry-analytics' in content, "No se encontró Time Series Insights"
    assert 'dt-smart-building' in content, "No se encontró Digital Twins"
    
    # Verificar recursos de red avanzados
    assert 'er-primary-circuit' in content, "No se encontró ExpressRoute"
    assert 'privatelink.database.windows.net' in content, "No se encontró Private DNS Zone"
    assert 'fd-global-cdn' in content, "No se encontró Front Door"
    
    # Verificar recursos poco comunes
    assert 'anf-high-performance' in content, "No se encontró NetApp Files"
    assert 'hpc-ml-cache' in content, "No se encontró HPC Cache"
    assert 'batch-ml-training' in content, "No se encontró Azure Batch"
    
    # Verificar tipos de líneas
    assert 'strokeColor=#1976d2;strokeWidth=2;' in content, "No se encontraron líneas jerárquicas"
    assert 'dashed=1;' in content, "No se encontraron líneas de relación"
    
    # Guardar archivo de prueba
    output_file = 'test-edge-cases-specialized.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test de casos edge completado exitosamente")
    print(f"📁 Archivo generado: {output_file}")
    print(f"📏 Tamaño del contenido: {len(content)} caracteres")
    print(f"🎯 Resultado: Algoritmo DFS maneja recursos especializados y casos edge correctamente")

def test_massive_scale_simulation():
    """Test de escalabilidad con simulación de estructura masiva"""
    
    import time
    
    print("🧪 Simulando estructura empresarial masiva...")
    
    # Generar una estructura muy grande programáticamente
    massive_items = []
    massive_dependencies = []
    
    # 10 Management Groups
    for i in range(10):
        mg_id = f'/providers/Microsoft.Management/managementGroups/mg-division-{i:02d}'
        massive_items.append({
            'id': mg_id,
            'name': f'Division {i:02d}',
            'type': 'Microsoft.Management/managementGroups'
        })
        
        # Parent hierarchy
        if i > 0:
            parent_id = f'/providers/Microsoft.Management/managementGroups/mg-division-{(i-1):02d}'
            massive_dependencies.append((mg_id, parent_id))
    
    # 50 Subscriptions
    for i in range(50):
        sub_id = f'/subscriptions/sub-workload-{i:03d}'
        massive_items.append({
            'id': sub_id,
            'name': f'Workload Subscription {i:03d}',
            'type': 'Microsoft.Resources/subscriptions'
        })
        
        # Assign to MG (distribute evenly)
        mg_index = i % 10
        mg_id = f'/providers/Microsoft.Management/managementGroups/mg-division-{mg_index:02d}'
        massive_dependencies.append((sub_id, mg_id))
    
    # 200 Resource Groups (4 per subscription)
    for sub_i in range(50):
        sub_id = f'/subscriptions/sub-workload-{sub_i:03d}'
        for rg_i in range(4):
            rg_id = f'{sub_id}/resourceGroups/rg-app-{rg_i+1:02d}'
            massive_items.append({
                'id': rg_id,
                'name': f'rg-app-{rg_i+1:02d}',
                'type': 'Microsoft.Resources/subscriptions/resourceGroups'
            })
            massive_dependencies.append((rg_id, sub_id))
    
    # 800 Resources (4 per RG)
    resource_types = [
        'Microsoft.Network/virtualNetworks',
        'Microsoft.Compute/virtualMachines',
        'Microsoft.Storage/storageAccounts',
        'Microsoft.Web/sites'
    ]
    
    for sub_i in range(50):
        for rg_i in range(4):
            rg_id = f'/subscriptions/sub-workload-{sub_i:03d}/resourceGroups/rg-app-{rg_i+1:02d}'
            for res_i in range(4):
                res_type = resource_types[res_i]
                provider = res_type.split('/')[0]
                resource_type = res_type.split('/')[1]
                
                res_id = f'{rg_id}/providers/{provider}/{resource_type}/resource-{res_i+1:02d}'
                massive_items.append({
                    'id': res_id,
                    'name': f'resource-{res_i+1:02d}',
                    'type': res_type
                })
                massive_dependencies.append((res_id, rg_id))
    
    print(f"📊 Estructura masiva generada:")
    print(f"   • Management Groups: 10")
    print(f"   • Subscriptions: 50")
    print(f"   • Resource Groups: 200")
    print(f"   • Resources: 800")
    print(f"   • Total items: {len(massive_items)}")
    print(f"   • Total dependencies: {len(massive_dependencies)}")
    
    start_time = time.time()
    
    content = generate_drawio_file(
        massive_items, 
        massive_dependencies, 
        embed_data=False,
        include_ids=None,
        diagram_mode='infrastructure'
    )
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Verificaciones de escalabilidad
    assert content is not None, "No se generó contenido"
    assert len(content) > 10000, "El contenido es demasiado corto para una estructura masiva"
    
    # Guardar archivo de prueba
    output_file = 'test-massive-scale.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Test de escalabilidad completado")
    print(f"📁 Archivo generado: {output_file}")
    print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos")
    print(f"📏 Tamaño del contenido: {len(content)} caracteres")
    print(f"📈 Rendimiento: {len(massive_items)/execution_time:.0f} items/segundo")
    
    if execution_time > 30:
        print("⚠️  Tiempo elevado - el algoritmo podría necesitar optimización para estructuras muy grandes")
    elif execution_time > 10:
        print("⚡ Rendimiento aceptable para estructuras grandes")
    else:
        print("🚀 Excelente rendimiento para estructuras masivas")

if __name__ == "__main__":
    try:
        test_edge_cases_and_specialized_resources()
        test_massive_scale_simulation()
        print("\n🎉 TODOS LOS TESTS DE CASOS EDGE Y ESCALABILIDAD PASARON CORRECTAMENTE")
    except Exception as e:
        print(f"\n❌ ERROR en tests avanzados: {e}")
        import traceback
        traceback.print_exc()
        raise

#!/usr/bin/env python3
"""
Genera un inventario Azure complejo y realista (enmascarado) para probar el
pipeline completo: src/cli.py --input-json <archivo> --diagram-mode all

Cubre a proposito:
  - Jerarquia de 2 niveles de Management Groups + 2 suscripciones + 7 Resource Groups.
  - Topologia de red hub-spoke con NSG y Route Table asignados a MULTIPLES subnets
    (para ejercitar los elementos virtuales "(asignacion)" del modo network).
  - Un recurso de tipo "hidden" (privateDnsZones/virtualNetworkLinks).
  - ~35 tipos de recurso nuevos anadidos recientemente a AZURE_ICONS
    (Cosmos DB, Synapse, Databricks, Event Hub, IoT Hub, Digital Twins, Purview,
    Data Explorer, PostgreSQL flexible server, Redis, Front Door, NAT Gateway,
    Container Apps, Batch, Azure Spring Apps, Sentinel, Defender, etc.)

Uso:
  python examples/generate_complex_example_inventory.py
  python src/cli.py --input-json data/complex_example_inventory.json --diagram-mode all --all-tenants --output complex_render.drawio
"""

import json
import os
import sys
from datetime import datetime, timezone

TENANT_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
SUB_PROD = "11111111-1111-1111-1111-111111111111"
SUB_SHARED = "22222222-2222-2222-2222-222222222222"

items = []
dependencies = []


def add_item(id_, type_, name, resource_group=None, subscription_id=None, location=None, properties=None):
    item = {"id": id_, "type": type_, "name": name, "tenantId": TENANT_ID}
    if location:
        item["location"] = location
    if resource_group:
        item["resourceGroup"] = resource_group
    if subscription_id:
        item["subscriptionId"] = subscription_id
    item["properties"] = properties or {}
    items.append(item)
    return id_


def add_dep(child_id, parent_id):
    dependencies.append([child_id, parent_id])


# --- Management Groups y suscripciones ---
mg_root = add_item(
    "/providers/Microsoft.Management/managementGroups/mg-contoso-root",
    "microsoft.management/managementgroups", "mg-contoso-root")
mg_lz = add_item(
    "/providers/Microsoft.Management/managementGroups/mg-contoso-landingzones",
    "microsoft.management/managementgroups", "mg-contoso-landingzones",
    properties={"details": {"managementGroupAncestorsChain": [{"id": mg_root}]}})
add_dep(mg_lz, mg_root)

sub_prod = add_item(f"/subscriptions/{SUB_PROD}", "microsoft.resources/subscriptions", "sub-prod-eu",
                     properties={"managementGroupAncestorsChain": [{"id": mg_lz}]})
sub_shared = add_item(f"/subscriptions/{SUB_SHARED}", "microsoft.resources/subscriptions", "sub-shared-eu",
                       properties={"managementGroupAncestorsChain": [{"id": mg_lz}]})
add_dep(sub_prod, mg_lz)
add_dep(sub_shared, mg_lz)

RG_DEFS = [
    ("rg-network-hub-we", SUB_SHARED, sub_shared, "westeurope"),
    ("rg-network-spoke-we", SUB_PROD, sub_prod, "westeurope"),
    ("rg-compute-prod-we", SUB_PROD, sub_prod, "westeurope"),
    ("rg-data-prod-we", SUB_PROD, sub_prod, "westeurope"),
    ("rg-ai-prod-we", SUB_PROD, sub_prod, "northeurope"),  # segunda regi\u00f3n en sub-prod
    ("rg-security-shared-we", SUB_SHARED, sub_shared, "westeurope"),
    ("rg-management-shared-we", SUB_SHARED, sub_shared, "northeurope"),  # segunda regi\u00f3n en sub-shared
]
rg_ids = {}
for rg_name, sub_id, sub_item_id, rg_location in RG_DEFS:
    rg_id = add_item(f"/subscriptions/{sub_id}/resourceGroups/{rg_name}",
                      "microsoft.resources/subscriptions/resourcegroups", rg_name,
                      subscription_id=sub_id, location=rg_location)
    rg_ids[rg_name] = rg_id
    add_dep(rg_id, sub_item_id)


def rg(name):
    return rg_ids[name]


def prov(rg_name, sub_id, provider_path):
    """Construye un ID de recurso realista bajo un RG."""
    return f"/subscriptions/{sub_id}/resourceGroups/{rg_name}/providers/{provider_path}"


# --- Red: hub (rg-network-hub-we) ---
RG_HUB, RG_SPOKE = "rg-network-hub-we", "rg-network-spoke-we"

vnet_hub = add_item(prov(RG_HUB, SUB_SHARED, "Microsoft.Network/virtualNetworks/vnet-hub-we"),
                     "microsoft.network/virtualnetworks", "vnet-hub-we", RG_HUB, SUB_SHARED, "westeurope",
                     {"addressSpace": {"addressPrefixes": ["10.0.0.0/16"]}})
add_dep(vnet_hub, rg(RG_HUB))

snet_gateway = add_item(f"{vnet_hub}/subnets/snet-gateway-we",
                         "microsoft.network/virtualnetworks/subnets", "snet-gateway-we", RG_HUB, SUB_SHARED,
                         properties={"addressPrefix": "10.0.0.0/24"})
add_dep(snet_gateway, vnet_hub)

snet_shared = add_item(f"{vnet_hub}/subnets/snet-shared-we",
                        "microsoft.network/virtualnetworks/subnets", "snet-shared-we", RG_HUB, SUB_SHARED,
                        properties={"addressPrefix": "10.0.1.0/24"})
add_dep(snet_shared, vnet_hub)

pip_gw = add_item(prov(RG_HUB, SUB_SHARED, "Microsoft.Network/publicIPAddresses/pip-gateway-we"),
                   "microsoft.network/publicipaddresses", "pip-gateway-we", RG_HUB, SUB_SHARED, "westeurope",
                   {"publicIPAllocationMethod": "Static"})
add_dep(pip_gw, rg(RG_HUB))

vgw_hub = add_item(prov(RG_HUB, SUB_SHARED, "Microsoft.Network/virtualNetworkGateways/vgw-hub-we"),
                    "microsoft.network/virtualnetworkgateways", "vgw-hub-we", RG_HUB, SUB_SHARED, "westeurope",
                    {"ipConfigurations": [{"properties": {"subnet": {"id": snet_gateway}}}]})
add_dep(vgw_hub, rg(RG_HUB))
add_dep(vgw_hub, snet_gateway)

azfw_hub = add_item(prov(RG_HUB, SUB_SHARED, "Microsoft.Network/azureFirewalls/azfw-hub-we"),
                     "microsoft.network/azurefirewalls", "azfw-hub-we", RG_HUB, SUB_SHARED, "westeurope")
add_dep(azfw_hub, rg(RG_HUB))

pdnz = add_item(prov(RG_HUB, SUB_SHARED, "Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net"),
                 "microsoft.network/privatednszones", "privatelink.blob.core.windows.net", RG_HUB, SUB_SHARED)
add_dep(pdnz, rg(RG_HUB))

pdnz_link = add_item(f"{pdnz}/virtualNetworkLinks/link-to-hub",
                      "microsoft.network/privatednszones/virtualnetworklinks", "link-to-hub", RG_HUB, SUB_SHARED,
                      properties={"virtualNetwork": {"id": vnet_hub}})
add_dep(pdnz_link, pdnz)
add_dep(pdnz_link, vnet_hub)

# --- Red: spoke (rg-network-spoke-we) ---
vnet_spoke = add_item(prov(RG_SPOKE, SUB_PROD, "Microsoft.Network/virtualNetworks/vnet-spoke-we"),
                       "microsoft.network/virtualnetworks", "vnet-spoke-we", RG_SPOKE, SUB_PROD, "westeurope",
                       {"addressSpace": {"addressPrefixes": ["10.1.0.0/16"]}})
add_dep(vnet_spoke, rg(RG_SPOKE))

snet_app = add_item(f"{vnet_spoke}/subnets/snet-app-we",
                     "microsoft.network/virtualnetworks/subnets", "snet-app-we", RG_SPOKE, SUB_PROD,
                     properties={"addressPrefix": "10.1.0.0/24"})
add_dep(snet_app, vnet_spoke)

snet_data = add_item(f"{vnet_spoke}/subnets/snet-data-we",
                      "microsoft.network/virtualnetworks/subnets", "snet-data-we", RG_SPOKE, SUB_PROD,
                      properties={"addressPrefix": "10.1.1.0/24"})
add_dep(snet_data, vnet_spoke)

# NSG asignado a MULTIPLES subnets (cross-vnet) -> ejercita elementos "(asignacion)"
nsg_shared = add_item(prov(RG_HUB, SUB_SHARED, "Microsoft.Network/networkSecurityGroups/nsg-shared-we"),
                       "microsoft.network/networksecuritygroups", "nsg-shared-we", RG_HUB, SUB_SHARED, "westeurope",
                       {"subnets": [{"id": snet_shared}, {"id": snet_app}]})
add_dep(nsg_shared, rg(RG_HUB))

# Route Table asignada a MULTIPLES subnets del spoke
rt_shared = add_item(prov(RG_HUB, SUB_SHARED, "Microsoft.Network/routeTables/rt-shared-we"),
                      "microsoft.network/routetables", "rt-shared-we", RG_HUB, SUB_SHARED, "westeurope",
                      {"subnets": [{"id": snet_app}, {"id": snet_data}]})
add_dep(rt_shared, rg(RG_HUB))

nic_vm_web = add_item(prov(RG_SPOKE, SUB_PROD, "Microsoft.Network/networkInterfaces/nic-vm-web-we"),
                       "microsoft.network/networkinterfaces", "nic-vm-web-we", RG_SPOKE, SUB_PROD, "westeurope",
                       {"ipConfigurations": [{"properties": {"subnet": {"id": snet_app}}}]})
add_dep(nic_vm_web, rg(RG_SPOKE))
add_dep(nic_vm_web, snet_app)

lb_internal = add_item(prov(RG_SPOKE, SUB_PROD, "Microsoft.Network/loadBalancers/lb-internal-we"),
                        "microsoft.network/loadbalancers", "lb-internal-we", RG_SPOKE, SUB_PROD, "westeurope")
add_dep(lb_internal, rg(RG_SPOKE))

natgw_spoke = add_item(prov(RG_SPOKE, SUB_PROD, "Microsoft.Network/natGateways/natgw-spoke-we"),
                        "microsoft.network/natgateways", "natgw-spoke-we", RG_SPOKE, SUB_PROD, "westeurope")
add_dep(natgw_spoke, rg(RG_SPOKE))

frontdoor = add_item(prov(RG_SPOKE, SUB_PROD, "Microsoft.Network/frontdoors/fd-public-we"),
                      "microsoft.network/frontdoors", "fd-public-we", RG_SPOKE, SUB_PROD, "global",
                      {"backendPools": [{"backends": [{"privateLinkResourceId": prov("rg-compute-prod-we", SUB_PROD, "Microsoft.Web/sites/app-web-prod-we")}]}]})
add_dep(frontdoor, rg(RG_SPOKE))

asg_app = add_item(prov(RG_SPOKE, SUB_PROD, "Microsoft.Network/applicationSecurityGroups/asg-app-we"),
                    "microsoft.network/applicationsecuritygroups", "asg-app-we", RG_SPOKE, SUB_PROD, "westeurope")
add_dep(asg_app, rg(RG_SPOKE))

# --- Compute (rg-compute-prod-we) ---
RG_COMPUTE = "rg-compute-prod-we"
disk_vm_web = add_item(prov(RG_COMPUTE, SUB_PROD, "Microsoft.Compute/disks/vm-web-prod-we-osdisk"),
                        "microsoft.compute/disks", "vm-web-prod-we-osdisk", RG_COMPUTE, SUB_PROD, "westeurope")
add_dep(disk_vm_web, rg(RG_COMPUTE))

vm_web = add_item(prov(RG_COMPUTE, SUB_PROD, "Microsoft.Compute/virtualMachines/vm-web-prod-we"),
                   "microsoft.compute/virtualmachines", "vm-web-prod-we", RG_COMPUTE, SUB_PROD, "westeurope",
                   {"networkProfile": {"networkInterfaces": [{"id": nic_vm_web}]},
                    "storageProfile": {"osDisk": {"managedDisk": {"id": disk_vm_web}}}})
add_dep(vm_web, rg(RG_COMPUTE))
add_dep(vm_web, nic_vm_web)
add_dep(vm_web, disk_vm_web)

vmss_app = add_item(prov(RG_COMPUTE, SUB_PROD, "Microsoft.Compute/virtualMachineScaleSets/vmss-app-prod-we"),
                     "microsoft.compute/virtualmachinescalesets", "vmss-app-prod-we", RG_COMPUTE, SUB_PROD, "westeurope")
add_dep(vmss_app, rg(RG_COMPUTE))

aks_prod = add_item(prov(RG_COMPUTE, SUB_PROD, "Microsoft.ContainerService/managedClusters/aks-prod-we"),
                     "microsoft.containerservice/managedclusters", "aks-prod-we", RG_COMPUTE, SUB_PROD, "westeurope")
add_dep(aks_prod, rg(RG_COMPUTE))

batch_prod = add_item(prov(RG_COMPUTE, SUB_PROD, "Microsoft.Batch/batchAccounts/batchprodwe"),
                       "microsoft.batch/batchaccounts", "batchprodwe", RG_COMPUTE, SUB_PROD, "westeurope")
add_dep(batch_prod, rg(RG_COMPUTE))

cae_prod = add_item(prov(RG_COMPUTE, SUB_PROD, "Microsoft.App/managedEnvironments/cae-prod-we"),
                     "microsoft.app/managedenvironments", "cae-prod-we", RG_COMPUTE, SUB_PROD, "westeurope")
add_dep(cae_prod, rg(RG_COMPUTE))

ca_api = add_item(prov(RG_COMPUTE, SUB_PROD, "Microsoft.App/containerApps/ca-api-prod-we"),
                   "microsoft.app/containerapps", "ca-api-prod-we", RG_COMPUTE, SUB_PROD, "westeurope",
                   {"environmentId": cae_prod})
add_dep(ca_api, rg(RG_COMPUTE))
add_dep(ca_api, cae_prod)

asp_web = add_item(prov(RG_COMPUTE, SUB_PROD, "Microsoft.Web/serverfarms/asp-web-prod-we"),
                    "microsoft.web/serverfarms", "asp-web-prod-we", RG_COMPUTE, SUB_PROD, "westeurope")
add_dep(asp_web, rg(RG_COMPUTE))

app_web = add_item(prov(RG_COMPUTE, SUB_PROD, "Microsoft.Web/sites/app-web-prod-we"),
                    "microsoft.web/sites", "app-web-prod-we", RG_COMPUTE, SUB_PROD, "westeurope",
                    {"serverFarmId": asp_web})
add_dep(app_web, rg(RG_COMPUTE))
add_dep(app_web, asp_web)

spring_prod = add_item(prov(RG_COMPUTE, SUB_PROD, "Microsoft.AppPlatform/Spring/spring-prod-we"),
                        "microsoft.appplatform/spring", "spring-prod-we", RG_COMPUTE, SUB_PROD, "westeurope")
add_dep(spring_prod, rg(RG_COMPUTE))

# --- Data (rg-data-prod-we) ---
RG_DATA = "rg-data-prod-we"
storage_prod = add_item(prov(RG_DATA, SUB_PROD, "Microsoft.Storage/storageAccounts/stprodwe001"),
                         "microsoft.storage/storageaccounts", "stprodwe001", RG_DATA, SUB_PROD, "westeurope")
add_dep(storage_prod, rg(RG_DATA))

storage_blob = add_item(f"{storage_prod}/blobServices/default",
                         "microsoft.storage/storageaccounts/blobservices", "default", RG_DATA, SUB_PROD)
add_dep(storage_blob, storage_prod)

pe_storage = add_item(prov(RG_SPOKE, SUB_PROD, "Microsoft.Network/privateEndpoints/pe-storage-we"),
                       "microsoft.network/privateendpoints", "pe-storage-we", RG_SPOKE, SUB_PROD, "westeurope",
                       {"subnet": {"id": snet_data},
                        "privateLinkServiceConnections": [{"properties": {"privateLinkServiceId": storage_prod}}]})
add_dep(pe_storage, rg(RG_SPOKE))
add_dep(pe_storage, snet_data)
add_dep(pe_storage, storage_prod)

cosmos_prod = add_item(prov(RG_DATA, SUB_PROD, "Microsoft.DocumentDB/databaseAccounts/cosmos-prod-we"),
                        "microsoft.documentdb/databaseaccounts", "cosmos-prod-we", RG_DATA, SUB_PROD, "westeurope")
add_dep(cosmos_prod, rg(RG_DATA))

sql_server = add_item(prov(RG_DATA, SUB_PROD, "Microsoft.Sql/servers/sql-prod-we"),
                       "microsoft.sql/servers", "sql-prod-we", RG_DATA, SUB_PROD, "westeurope")
add_dep(sql_server, rg(RG_DATA))

sql_db = add_item(f"{sql_server}/databases/sqldb-app-prod-we",
                   "microsoft.sql/servers/databases", "sqldb-app-prod-we", RG_DATA, SUB_PROD, "westeurope")
add_dep(sql_db, sql_server)

psql_flex = add_item(prov(RG_DATA, SUB_PROD, "Microsoft.DBforPostgreSQL/flexibleServers/psql-prod-we"),
                      "microsoft.dbforpostgresql/flexibleservers", "psql-prod-we", RG_DATA, SUB_PROD, "westeurope")
add_dep(psql_flex, rg(RG_DATA))

redis_prod = add_item(prov(RG_DATA, SUB_PROD, "Microsoft.Cache/redis/redis-prod-we"),
                       "microsoft.cache/redis", "redis-prod-we", RG_DATA, SUB_PROD, "westeurope")
add_dep(redis_prod, rg(RG_DATA))

synapse_prod = add_item(prov(RG_DATA, SUB_PROD, "Microsoft.Synapse/workspaces/synapse-prod-we"),
                         "microsoft.synapse/workspaces", "synapse-prod-we", RG_DATA, SUB_PROD, "westeurope")
add_dep(synapse_prod, rg(RG_DATA))

adf_prod = add_item(prov(RG_DATA, SUB_PROD, "Microsoft.DataFactory/factories/adf-prod-we"),
                     "microsoft.datafactory/factories", "adf-prod-we", RG_DATA, SUB_PROD, "westeurope")
add_dep(adf_prod, rg(RG_DATA))

databricks_prod = add_item(prov(RG_DATA, SUB_PROD, "Microsoft.Databricks/workspaces/databricks-prod-we"),
                            "microsoft.databricks/workspaces", "databricks-prod-we", RG_DATA, SUB_PROD, "westeurope")
add_dep(databricks_prod, rg(RG_DATA))

eh_ns = add_item(prov(RG_DATA, SUB_PROD, "Microsoft.EventHub/namespaces/eh-ns-prod-we"),
                  "microsoft.eventhub/namespaces", "eh-ns-prod-we", RG_DATA, SUB_PROD, "westeurope")
add_dep(eh_ns, rg(RG_DATA))

eh_telemetry = add_item(f"{eh_ns}/eventhubs/eh-telemetry-prod-we",
                         "microsoft.eventhub/namespaces/eventhubs", "eh-telemetry-prod-we", RG_DATA, SUB_PROD)
add_dep(eh_telemetry, eh_ns)

purview_prod = add_item(prov(RG_DATA, SUB_PROD, "Microsoft.Purview/accounts/purview-prod-we"),
                         "microsoft.purview/accounts", "purview-prod-we", RG_DATA, SUB_PROD, "westeurope")
add_dep(purview_prod, rg(RG_DATA))

kusto_prod = add_item(prov(RG_DATA, SUB_PROD, "Microsoft.Kusto/clusters/kusto-prod-we"),
                       "microsoft.kusto/clusters", "kusto-prod-we", RG_DATA, SUB_PROD, "westeurope")
add_dep(kusto_prod, rg(RG_DATA))

# --- AI / IoT (rg-ai-prod-we) ---
RG_AI = "rg-ai-prod-we"
cog_prod = add_item(prov(RG_AI, SUB_PROD, "Microsoft.CognitiveServices/accounts/cog-prod-we"),
                     "microsoft.cognitiveservices/accounts", "cog-prod-we", RG_AI, SUB_PROD, "westeurope")
add_dep(cog_prod, rg(RG_AI))

mlw_prod = add_item(prov(RG_AI, SUB_PROD, "Microsoft.MachineLearningServices/workspaces/mlw-prod-we"),
                     "microsoft.machinelearningservices/workspaces", "mlw-prod-we", RG_AI, SUB_PROD, "westeurope")
add_dep(mlw_prod, rg(RG_AI))

iothub_prod = add_item(prov(RG_AI, SUB_PROD, "Microsoft.Devices/IotHubs/iothub-prod-we"),
                        "microsoft.devices/iothubs", "iothub-prod-we", RG_AI, SUB_PROD, "westeurope")
add_dep(iothub_prod, rg(RG_AI))

dt_prod = add_item(prov(RG_AI, SUB_PROD, "Microsoft.DigitalTwins/digitalTwinsInstances/dt-prod-we"),
                    "microsoft.digitaltwins/digitaltwinsinstances", "dt-prod-we", RG_AI, SUB_PROD, "westeurope")
add_dep(dt_prod, rg(RG_AI))
add_dep(dt_prod, iothub_prod)

maps_prod = add_item(prov(RG_AI, SUB_PROD, "Microsoft.Maps/accounts/maps-prod-we"),
                      "microsoft.maps/accounts", "maps-prod-we", RG_AI, SUB_PROD, "westeurope")
add_dep(maps_prod, rg(RG_AI))

bot_prod = add_item(prov(RG_AI, SUB_PROD, "Microsoft.BotService/botServices/bot-prod-we"),
                     "microsoft.botservice/botservices", "bot-prod-we", RG_AI, SUB_PROD, "global")
add_dep(bot_prod, rg(RG_AI))

# --- Seguridad (rg-security-shared-we) ---
RG_SEC = "rg-security-shared-we"
kv_shared = add_item(prov(RG_SEC, SUB_SHARED, "Microsoft.KeyVault/vaults/kv-shared-we"),
                      "microsoft.keyvault/vaults", "kv-shared-we", RG_SEC, SUB_SHARED, "westeurope")
add_dep(kv_shared, rg(RG_SEC))

law_shared = add_item(prov(RG_SEC, SUB_SHARED, "Microsoft.OperationalInsights/workspaces/law-shared-we"),
                       "microsoft.operationalinsights/workspaces", "law-shared-we", RG_SEC, SUB_SHARED, "westeurope")
add_dep(law_shared, rg(RG_SEC))

appi_shared = add_item(prov(RG_SEC, SUB_SHARED, "Microsoft.Insights/components/appi-shared-we"),
                        "microsoft.insights/components", "appi-shared-we", RG_SEC, SUB_SHARED, "westeurope",
                        {"WorkspaceResourceId": law_shared})
add_dep(appi_shared, rg(RG_SEC))
add_dep(appi_shared, law_shared)

rsv_shared = add_item(prov(RG_SEC, SUB_SHARED, "Microsoft.RecoveryServices/vaults/rsv-shared-we"),
                       "microsoft.recoveryservices/vaults", "rsv-shared-we", RG_SEC, SUB_SHARED, "westeurope")
add_dep(rsv_shared, rg(RG_SEC))

defender_pricing = add_item(f"/subscriptions/{SUB_SHARED}/providers/Microsoft.Security/pricings/VirtualMachines",
                             "microsoft.security/pricings", "VirtualMachines", subscription_id=SUB_SHARED)
add_dep(defender_pricing, sub_shared)

sentinel_shared = add_item(f"{law_shared}/providers/Microsoft.SecurityInsights/solutions/sentinel-shared-we",
                            "microsoft.securityinsights/solutions", "sentinel-shared-we", RG_SEC, SUB_SHARED)
add_dep(sentinel_shared, law_shared)

# --- Gestion (rg-management-shared-we) ---
RG_MGMT = "rg-management-shared-we"
aa_shared = add_item(prov(RG_MGMT, SUB_SHARED, "Microsoft.Automation/automationAccounts/aa-shared-we"),
                      "microsoft.automation/automationaccounts", "aa-shared-we", RG_MGMT, SUB_SHARED, "westeurope")
add_dep(aa_shared, rg(RG_MGMT))

media_shared = add_item(prov(RG_MGMT, SUB_SHARED, "Microsoft.Media/mediaservices/media-shared-we"),
                         "microsoft.media/mediaservices", "media-shared-we", RG_MGMT, SUB_SHARED, "westeurope")
add_dep(media_shared, rg(RG_MGMT))


def main():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from azure_api import find_dependencies

    # Las dependencias reales que se exportan vienen de find_dependencies(), la
    # misma funcion que usa la herramienta con datos reales de Azure Resource Graph
    # (no de la lista `dependencies` anotada a mano arriba, que solo documenta la
    # intencion junto a cada recurso para quien lea este generador).
    real_dependencies = find_dependencies(items)
    print(f"INFO: find_dependencies() detecto {len(real_dependencies)} dependencias reales "
          f"(vs {len(dependencies)} anotadas a mano en este generador, solo documentales)")

    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "complex_example_inventory.json")
    output_path = os.path.abspath(output_path)
    export_data = {
        "metadata": {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "source": "generate_complex_example_inventory.py",
            "total_items": len(items),
            "total_dependencies": len(real_dependencies),
        },
        "items": items,
        "dependencies": [list(dep) for dep in real_dependencies],
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    print(f"OK: {len(items)} recursos, {len(real_dependencies)} dependencias -> {output_path}")


if __name__ == "__main__":
    main()

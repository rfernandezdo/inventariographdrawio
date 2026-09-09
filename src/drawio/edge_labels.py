"""
Etiquetas descriptivas para las aristas (dependencias) de los diagramas.

Deriva un texto corto que explica la relación entre dos recursos concretos
(ej. "Subnet", "App Service Plan", "Private Link") a partir de sus tipos de
Azure, sin necesitar cambiar el esquema de `dependencies` (sigue siendo una
lista de tuplas (src_id, tgt_id)). Se usa en los modos 'components' y
'network', donde las aristas representan integraciones tecnológicas reales
(ver skill validate-azure-icons y la definición de "Component diagram" de
https://learn.microsoft.com/azure/well-architected/architect-role/design-diagrams).
"""

# Etiqueta por defecto según el tipo de recurso DESTINO de la dependencia
# (src depende de tgt: la etiqueta describe qué papel juega tgt para src).
_TARGET_TYPE_LABELS = {
    "microsoft.network/virtualnetworks/subnets": "Subnet",
    "microsoft.network/virtualnetworks": "VNet",
    "microsoft.web/serverfarms": "App Service Plan",
    "microsoft.sql/servers": "SQL Server",
    "microsoft.app/managedenvironments": "Container App Environment",
    "microsoft.operationalinsights/workspaces": "Log Analytics",
    "microsoft.devices/iothubs": "IoT Hub",
    "microsoft.eventhub/namespaces": "Event Hub Namespace",
    "microsoft.network/privatednszones": "DNS Zone",
    "microsoft.storage/storageaccounts": "Storage Account",
    "microsoft.keyvault/vaults": "Key Vault",
    "microsoft.managedidentity/userassignedidentities": "Managed Identity",
    "microsoft.network/networkinterfaces": "NIC",
}

# Pares (source_type, target_type) con un significado más específico que el
# genérico de _TARGET_TYPE_LABELS.
_PAIR_LABELS = {
    ("microsoft.network/privateendpoints", "microsoft.network/virtualnetworks/subnets"): "Private Link",
    ("microsoft.network/networksecuritygroups", "microsoft.network/virtualnetworks/subnets"): "Association",
    ("microsoft.network/routetables", "microsoft.network/virtualnetworks/subnets"): "Association",
    ("microsoft.network/virtualnetworkgateways", "microsoft.network/virtualnetworks/subnets"): "Gateway Subnet",
    ("microsoft.network/privatednszones/virtualnetworklinks", "microsoft.network/virtualnetworks"): "VNet Link",
}


def describe_relationship(source_type, target_type):
    """
    Devuelve una etiqueta corta que describe la relación entre dos tipos de
    recurso de Azure, o cadena vacía si no hay una descripción conocida.

    Args:
        source_type: Tipo de recurso origen (el que depende del destino)
        target_type: Tipo de recurso destino

    Returns:
        str: Etiqueta descriptiva (puede ser vacía)
    """
    s = (source_type or "").lower()
    t = (target_type or "").lower()

    if s == "microsoft.network/virtualnetworks" and t == "microsoft.network/virtualnetworks":
        return "Peering"

    if s == "microsoft.network/privateendpoints" and t != "microsoft.network/virtualnetworks/subnets":
        return "Private Link"

    pair_label = _PAIR_LABELS.get((s, t))
    if pair_label:
        return pair_label

    return _TARGET_TYPE_LABELS.get(t, "")

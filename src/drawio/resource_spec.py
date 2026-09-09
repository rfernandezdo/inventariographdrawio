"""
Extrae una línea de "ficha técnica" corta por recurso (SKU/tier + ubicación,
y tags si existen), usada por el modo 'lld' para anotar cada nodo con el
detalle que un Low-Level Design debe comunicar (tecnología concreta
desplegada + "Resource Naming & Tagging", según la guía de referencia de
LinkedIn "How Azure Architect Creating HLD & LLD Document's"), sin necesitar
reglas por tipo de recurso: la mayoría de recursos de Azure Resource Graph
exponen un campo 'sku' de nivel superior con 'name'/'tier', y un campo 'tags'.
"""


def describe_resource_spec(item):
    """
    Devuelve una cadena corta tipo "Standard_GRS · westeurope" o None si el
    recurso no aporta información técnica adicional relevante.
    """
    parts = []

    sku = item.get('sku')
    if isinstance(sku, dict):
        sku_name = sku.get('name') or sku.get('tier')
        if sku_name:
            parts.append(str(sku_name))

    location = item.get('location')
    if location and location != 'global':
        parts.append(str(location))

    if not parts:
        return None
    return ' · '.join(parts)


def describe_resource_tags(item, max_tags=2):
    """
    Devuelve una cadena corta con hasta `max_tags` tags tipo "env=sandpit,
    tfstate=level0", o None si el recurso no tiene tags.
    """
    tags = item.get('tags')
    if not isinstance(tags, dict) or not tags:
        return None
    pairs = [f"{k}={v}" for k, v in list(tags.items())[:max_tags]]
    suffix = f" (+{len(tags) - max_tags})" if len(tags) > max_tags else ""
    return ', '.join(pairs) + suffix

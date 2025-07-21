"""
Estilos y configuración visual para Azure draw.io
"""

from .icons import HIDDEN_RESOURCE_TYPES, AZURE_ICONS

# Estilo especial para recursos hidden
HIDDEN_RESOURCE_STYLE = "verticalLabelPosition=bottom;verticalAlign=top;html=1;shape=mxgraph.infographic.shadedCube;isoAngle=15;fillColor=#10739E;strokeColor=none;aspect=fixed;"

# Estilos fallback para diferentes tipos de recursos
FALLBACK_STYLES = {
    "managementgroup": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;shadow=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=14;",
    "subscription": "rounded=1;whiteSpace=wrap;html=1;shadow=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=12;",
    "resourcegroup": "image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image=img/lib/azure2/general/Resource_Groups.svg;",
    "resource": "rounded=1;whiteSpace=wrap;html=1;shadow=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
}


def get_node_style(resource_type):
    """
    Obtiene el estilo apropiado para un tipo de recurso dado.
    
    Args:
        resource_type (str): Tipo de recurso de Azure
        
    Returns:
        str: Cadena de estilo para draw.io
    """
    if not resource_type:
        return FALLBACK_STYLES['resource']
    
    resource_type_lower = resource_type.lower()
    
    # Verificar si es un recurso hidden
    if resource_type_lower in HIDDEN_RESOURCE_TYPES:
        print(f"🔒 Aplicando estilo hidden a recurso: {resource_type}")
        return HIDDEN_RESOURCE_STYLE
    
    # Obtener icono específico de Azure
    icon_path = AZURE_ICONS.get(resource_type_lower)
    if icon_path:
        return f"image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image={icon_path}"
    
    # Estilos especiales para tipos de contenedores
    if resource_type_lower == 'microsoft.management/managementgroups': 
        return FALLBACK_STYLES['managementgroup']
    if resource_type_lower == 'microsoft.resources/subscriptions': 
        return FALLBACK_STYLES['subscription']
    if resource_type_lower == 'microsoft.resources/subscriptions/resourcegroups': 
        return FALLBACK_STYLES['resourcegroup']
    
    # Estilo genérico para recursos sin icono específico
    return FALLBACK_STYLES['resource']

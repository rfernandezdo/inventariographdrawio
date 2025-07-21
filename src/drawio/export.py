"""
Funciones principales de exportación a draw.io
Orchestación de layouts y generación de archivos finales
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import json

from .icons import AZURE_ICONS, HIDDEN_RESOURCE_TYPES
from .styles import get_node_style, HIDDEN_RESOURCE_STYLE
from .xml_builder import pretty_print_xml
from .layouts import generate_infrastructure_layout, generate_components_layout, generate_network_layout


def filter_items_and_dependencies(items, dependencies, include_ids=None, exclude_ids=None):
    """
    Filtra items y dependencias basado en IDs específicos a incluir/excluir.
    
    Args:
        items: Lista de recursos
        dependencies: Lista de dependencias  
        include_ids: Lista de IDs a incluir (si se especifica, solo estos se incluyen)
        exclude_ids: Lista de IDs a excluir
    
    Returns:
        tuple: (filtered_items, filtered_dependencies)
    """
    if include_ids is None and exclude_ids is None:
        return items, dependencies
    
    # Normalizar IDs para comparación
    if include_ids:
        include_ids_norm = {id.lower() for id in include_ids}
        filtered_items = [item for item in items if item.get('id', '').lower() in include_ids_norm]
    else:
        filtered_items = items
    
    if exclude_ids:
        exclude_ids_norm = {id.lower() for id in exclude_ids}
        filtered_items = [item for item in filtered_items if item.get('id', '').lower() not in exclude_ids_norm]
    
    # Crear conjunto de IDs filtrados para filtrar dependencias
    filtered_ids = {item.get('id', '').lower() for item in filtered_items}
    
    # Filtrar dependencias
    filtered_dependencies = [
        (src, tgt) for src, tgt in dependencies 
        if src.lower() in filtered_ids and tgt.lower() in filtered_ids
    ]
    
    return filtered_items, filtered_dependencies


def generate_drawio_file(items, dependencies, embed_data=True, include_ids=None, 
                        diagram_mode='infrastructure', no_hierarchy_edges=False):
    """
    Genera un archivo draw.io con un solo diagrama según el modo especificado.
    
    Args:
        items: Lista de recursos de Azure
        dependencies: Lista de dependencias entre recursos
        embed_data: Si incrustar datos completos o solo el tipo
        include_ids: IDs específicos a incluir
        diagram_mode: Tipo de diagrama ('infrastructure', 'components', 'network')
        no_hierarchy_edges: Si filtrar enlaces jerárquicos
    
    Returns:
        str: Contenido XML del archivo draw.io
    """
    print(f"INFO: Generando archivo draw.io en modo '{diagram_mode}'...")
    
    # Filtrar items y dependencias si se especifica
    if include_ids:
        items, dependencies = filter_items_and_dependencies(items, dependencies, include_ids=include_ids)
        print(f"INFO: Filtrado aplicado. {len(items)} items, {len(dependencies)} dependencias")
    
    # TODO: Implementar el resto de la función
    # Esta función necesita ser extraída completamente desde drawio_export.py
    
    return "<!-- Implementación pendiente -->"


def generate_drawio_multipage_file(items, dependencies, embed_data=True, include_ids=None, 
                                  no_hierarchy_edges=False):
    """
    Genera un archivo draw.io con múltiples páginas, cada una con un tipo de diagrama diferente.
    
    Args:
        items: Lista de recursos de Azure
        dependencies: Lista de dependencias entre recursos
        embed_data: Si incrustar datos completos o solo el tipo
        include_ids: IDs específicos a incluir
        no_hierarchy_edges: Si aplicar filtrado de enlaces jerárquicos (solo para página Network)
    
    Returns:
        str: Contenido XML del archivo draw.io con múltiples páginas
    """
    print("INFO: Generando archivo draw.io con múltiples páginas...")
    
    # TODO: Implementar el resto de la función
    # Esta función necesita ser extraída completamente desde drawio_export.py
    
    return "<!-- Implementación pendiente -->"

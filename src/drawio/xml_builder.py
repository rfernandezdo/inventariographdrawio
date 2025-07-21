"""
Utilidades para construir XML de draw.io
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom


def pretty_print_xml(elem):
    """
    Formatea el XML de manera legible.
    
    Args:
        elem: Elemento XML
        
    Returns:
        str: XML formateado
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def create_mxfile_root():
    """
    Crea el elemento raíz mxfile para draw.io.
    
    Returns:
        ET.Element: Elemento raíz mxfile
    """
    root = ET.Element("mxfile")
    root.set("host", "app.diagrams.net")
    root.set("modified", "2024-01-01T00:00:00.000Z")
    root.set("agent", "Azure Infrastructure Diagram Generator")
    root.set("version", "1.0")
    root.set("etag", "azure-generated")
    root.set("type", "device")
    return root


def create_diagram_element(name="Azure Infrastructure"):
    """
    Crea un elemento diagram para draw.io.
    
    Args:
        name (str): Nombre del diagrama
        
    Returns:
        ET.Element: Elemento diagram
    """
    diagram = ET.Element("diagram")
    diagram.set("name", name)
    diagram.set("id", f"azure-{name.lower().replace(' ', '-')}")
    return diagram


def create_mxgraphmodel_element():
    """
    Crea el elemento mxGraphModel.
    
    Returns:
        ET.Element: Elemento mxGraphModel
    """
    mxgraphmodel = ET.Element("mxGraphModel")
    mxgraphmodel.set("dx", "1426")
    mxgraphmodel.set("dy", "750")
    mxgraphmodel.set("grid", "1")
    mxgraphmodel.set("gridSize", "10")
    mxgraphmodel.set("guides", "1")
    mxgraphmodel.set("tooltips", "1")
    mxgraphmodel.set("connect", "1")
    mxgraphmodel.set("arrows", "1")
    mxgraphmodel.set("fold", "1")
    mxgraphmodel.set("page", "1")
    mxgraphmodel.set("pageScale", "1")
    mxgraphmodel.set("pageWidth", "827")
    mxgraphmodel.set("pageHeight", "1169")
    mxgraphmodel.set("math", "0")
    mxgraphmodel.set("shadow", "0")
    return mxgraphmodel


def create_root_element():
    """
    Crea el elemento root interno de mxGraphModel.
    
    Returns:
        ET.Element: Elemento root
    """
    root = ET.Element("root")
    
    # Crear células por defecto (0 y 1)
    mxcell_0 = ET.Element("mxCell")
    mxcell_0.set("id", "0")
    root.append(mxcell_0)
    
    mxcell_1 = ET.Element("mxCell")
    mxcell_1.set("id", "1")
    mxcell_1.set("parent", "0")
    root.append(mxcell_1)
    
    return root


def create_node_element(node_id, label, x, y, width=120, height=80, style="", parent_id="1", data=None):
    """
    Crea un elemento de nodo para draw.io.
    
    Args:
        node_id (str): ID único del nodo
        label (str): Etiqueta del nodo
        x (int): Posición X
        y (int): Posición Y
        width (int): Ancho del nodo
        height (int): Alto del nodo
        style (str): Estilo del nodo
        parent_id (str): ID del contenedor padre
        data (dict): Datos adicionales para embebido
        
    Returns:
        ET.Element: Elemento mxCell del nodo
    """
    mxcell = ET.Element("mxCell")
    mxcell.set("id", node_id)
    mxcell.set("value", label)
    mxcell.set("style", style)
    mxcell.set("vertex", "1")
    mxcell.set("parent", parent_id)
    
    # Agregar datos embebidos si se proporcionan
    if data:
        # Convertir datos a string para almacenar como atributo
        import json
        mxcell.set("azure_data", json.dumps(data))
    
    # Crear geometría
    geometry = ET.Element("mxGeometry")
    geometry.set("x", str(x))
    geometry.set("y", str(y))
    geometry.set("width", str(width))
    geometry.set("height", str(height))
    geometry.set("as", "geometry")
    
    mxcell.append(geometry)
    return mxcell


def create_edge_element(edge_id, source_id, target_id, style="", parent_id="1"):
    """
    Crea un elemento de conexión (edge) para draw.io.
    
    Args:
        edge_id (str): ID único de la conexión
        source_id (str): ID del nodo origen
        target_id (str): ID del nodo destino
        style (str): Estilo de la conexión
        parent_id (str): ID del contenedor padre
        
    Returns:
        ET.Element: Elemento mxCell de la conexión
    """
    mxcell = ET.Element("mxCell")
    mxcell.set("id", edge_id)
    mxcell.set("style", style)
    mxcell.set("edge", "1")
    mxcell.set("parent", parent_id)
    mxcell.set("source", source_id)
    mxcell.set("target", target_id)
    
    # Crear geometría básica para la conexión
    geometry = ET.Element("mxGeometry")
    geometry.set("relative", "1")
    geometry.set("as", "geometry")
    
    mxcell.append(geometry)
    return mxcell


def create_group_element(group_id, label, x, y, width, height, style="", parent_id="1"):
    """
    Crea un elemento de grupo/contenedor para draw.io.
    
    Args:
        group_id (str): ID único del grupo
        label (str): Etiqueta del grupo
        x (int): Posición X
        y (int): Posición Y
        width (int): Ancho del grupo
        height (int): Alto del grupo
        style (str): Estilo del grupo
        parent_id (str): ID del contenedor padre
        
    Returns:
        ET.Element: Elemento mxCell del grupo
    """
    mxcell = ET.Element("mxCell")
    mxcell.set("id", group_id)
    mxcell.set("value", label)
    mxcell.set("style", style)
    mxcell.set("vertex", "1")
    mxcell.set("parent", parent_id)
    mxcell.set("connectable", "0")  # Los grupos no son conectables directamente
    
    # Crear geometría
    geometry = ET.Element("mxGeometry")
    geometry.set("x", str(x))
    geometry.set("y", str(y))
    geometry.set("width", str(width))
    geometry.set("height", str(height))
    geometry.set("as", "geometry")
    
    mxcell.append(geometry)
    return mxcell

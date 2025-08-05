#!/usr/bin/env python3
"""
Generador simplificado de XML para demostrar NSGs y Route Tables multi-subnet
"""

import sys
import os
import json
import xml.etree.ElementTree as ET

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from drawio.layouts.network import generate_network_layout
from drawio.xml_builder import pretty_print_xml

def load_demo_data():
    """Carga los datos de demostración"""
    data_file = "data/demo_nsg_rt_multi_subnet.json"
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data['items'], data['dependencies']

def create_simple_diagram_xml(extended_items, node_positions, group_info, resource_to_parent_id):
    """Crea un XML simplificado de draw.io para demostrar el concepto"""
    
    # Crear estructura básica del XML
    mxfile = ET.Element("mxfile", 
                       host="app.diagrams.net", 
                       modified="2025-01-15T10:30:00.000Z",
                       agent="Demo NSG Multi-Subnet",
                       version="24.7.17")
    
    diagram = ET.SubElement(mxfile, "diagram", id="demo", name="Network Multi-Subnet Demo")
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel", 
                                dx="1426", dy="827", grid="1", gridSize="10",
                                guides="1", tooltips="1", connect="1", arrows="1",
                                fold="1", page="1", pageScale="1", pageWidth="827",
                                pageHeight="1169", math="0", shadow="0")
    
    root = ET.SubElement(mxGraphModel, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    
    # Crear contenedores
    for group in group_info:
        group_cell = ET.SubElement(root, "mxCell", 
                                 id=group['id'], 
                                 style=group['style'], 
                                 parent=group.get('parent_id', '1'), 
                                 vertex="1")
        ET.SubElement(group_cell, "mxGeometry", 
                     x=str(group['x']), y=str(group['y']),
                     width=str(group['width']), height=str(group['height']),
                     as_="geometry")
    
    # Crear nodos de recursos
    for i, item in enumerate(extended_items):
        if i not in node_positions:
            continue
            
        x, y = node_positions[i]
        parent_id = resource_to_parent_id.get(i, '1')
        
        # Determinar estilo según el tipo
        item_type = item.get('type', '').lower()
        if 'networksecuritygroups' in item_type:
            style = "image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image=img/lib/azure2/networking/Network_Security_Groups.svg"
        elif 'routetables' in item_type:
            style = "image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image=img/lib/azure2/networking/Route_Tables.svg"
        elif 'virtualnetworks' in item_type and 'subnets' not in item_type:
            style = "image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image=img/lib/azure2/networking/Virtual_Networks.svg"
        elif 'subnets' in item_type:
            style = "image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image=img/lib/azure2/networking/Subnet.svg"
        elif 'virtualmachines' in item_type:
            style = "image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image=img/lib/azure2/compute/Virtual_Machine.svg"
        elif 'servers' in item_type:
            style = "image;aspect=fixed;html=1;points=[];align=center;fontSize=12;labelBackgroundColor=none;image=img/lib/azure2/databases/SQL_Server.svg"
        else:
            style = "rounded=1;whiteSpace=wrap;html=1;fontSize=12;"
        
        # Crear cell del recurso
        cell_id = f"node-{i}"
        cell = ET.SubElement(root, "mxCell", 
                           id=cell_id,
                           style=style,
                           parent=parent_id,
                           vertex="1")
        
        # Geometry
        ET.SubElement(cell, "mxGeometry", 
                     x=str(x), y=str(y),
                     width="60", height="60",
                     as_="geometry")
        
        # Añadir datos como objeto
        object_elem = ET.SubElement(cell, "object")
        object_elem.set("label", f"<b>{item.get('name', 'Unknown')}</b>")
        object_elem.set("as", "value")
        object_elem.set("type", item.get('type', 'unknown'))
        object_elem.set("id", item.get('id', ''))
        
        # Marcar elementos virtuales
        if '_virtual_subnet_id' in item:
            object_elem.set("virtual_subnet", item['_virtual_subnet_id'])
            object_elem.set("original_index", str(item.get('_original_index', '')))
    
    return pretty_print_xml(mxfile)

def generate_demo():
    """Genera el diagrama de demostración"""
    
    print("🎯 Cargando datos de demostración...")
    items, dependencies = load_demo_data()
    
    print(f"📊 Datos cargados: {len(items)} recursos, {len(dependencies)} dependencias")
    
    # Estadísticas de elementos multi-subnet
    nsgs_multi = []
    rts_multi = []
    
    for item in items:
        item_type = item.get('type', '')
        if item_type == 'Microsoft.Network/networkSecurityGroups':
            subnets = item.get('properties', {}).get('subnets', [])
            if len(subnets) > 1:
                nsgs_multi.append(f"{item['name']} ({len(subnets)} subnets)")
        elif item_type == 'Microsoft.Network/routeTables':
            subnets = item.get('properties', {}).get('subnets', [])
            if len(subnets) > 1:
                rts_multi.append(f"{item['name']} ({len(subnets)} subnets)")
    
    print(f"\n🔒 NSGs multi-subnet: {', '.join(nsgs_multi)}")
    print(f"🛣️ Route Tables multi-subnet: {', '.join(rts_multi)}")
    
    print(f"\n🚀 Generando layout...")
    extended_items, node_positions, group_info, resource_to_parent_id = generate_network_layout(
        items, dependencies
    )
    
    print(f"✅ Layout completado: {len(extended_items)} elementos, {len(virtual := [i for i, item in enumerate(extended_items) if '_virtual_subnet_id' in item])} virtuales")
    
    # Mostrar elementos virtuales
    print(f"\n🔄 Elementos virtuales creados:")
    for i in virtual:
        item = extended_items[i]
        subnet_name = item['_virtual_subnet_id'].split('/')[-1]
        parent = resource_to_parent_id.get(i, 'sin padre')
        print(f"  • {item['name']} #{i} → {subnet_name} (padre: {parent})")
    
    print(f"\n🎨 Generando XML...")
    xml_content = create_simple_diagram_xml(extended_items, node_positions, group_info, resource_to_parent_id)
    
    # Guardar archivo
    output_file = "demo_nsg_rt_multi_subnet.drawio"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"✅ Diagrama guardado: {output_file}")
    
    # Verificaciones
    nsg_matches = xml_content.count('demo-nsg-web-tier') + xml_content.count('demo-nsg-data-tier')
    rt_matches = xml_content.count('demo-rt-shared') + xml_content.count('demo-rt-secure')
    virtual_matches = xml_content.count('virtual_subnet')
    
    print(f"\n🔍 Verificaciones:")
    print(f"  • NSGs en XML: {nsg_matches} menciones")
    print(f"  • Route Tables en XML: {rt_matches} menciones") 
    print(f"  • Elementos virtuales: {virtual_matches} marcados")
    
    return True

def main():
    print("🌐 Demo: NSGs y Route Tables Multi-Subnet")
    print("=" * 40)
    
    try:
        success = generate_demo()
        
        if success:
            print("\n🎉 ¡Demo generado exitosamente!")
            print("\n📁 Archivo: demo_nsg_rt_multi_subnet.drawio")
            print("\n💡 Qué verás:")
            print("  🔸 demo-nsg-web-tier aparece en 3 subnets diferentes")
            print("  🔸 demo-nsg-data-tier aparece en 2 subnets diferentes")
            print("  🔸 Cada instancia está posicionada en su subnet")
            print("  🔸 Los elementos virtuales están marcados en los metadatos")
            print("\n📖 Instrucciones:")
            print("  1. Abre demo_nsg_rt_multi_subnet.drawio en https://app.diagrams.net")
            print("  2. Observa como los NSGs aparecen duplicados correctamente")
            print("  3. Haz clic en un NSG virtual para ver sus metadatos")
            
            return 0
        else:
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

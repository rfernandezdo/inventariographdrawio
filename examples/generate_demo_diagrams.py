#!/usr/bin/env python3
"""
Generador de diagramas de demostración con NSGs y Route Tables multi-subnet
"""

import sys
import os
import json

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from drawio_export import generate_drawio_file

def load_demo_data():
    """Carga los datos de demostración"""
    data_file = "data/demo_nsg_rt_multi_subnet.json"
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data['items'], data['dependencies']

def generate_demo_diagrams():
    """Genera diagramas de demostración en diferentes modos"""
    
    print("🎯 Cargando datos de demostración...")
    items, dependencies = load_demo_data()
    
    print(f"📊 Datos cargados: {len(items)} recursos, {len(dependencies)} dependencias")
    
    # Mostrar estadísticas de los datos
    print("\n📈 Estadísticas:")
    
    resource_types = {}
    nsgs_multi_subnet = []
    route_tables_multi_subnet = []
    
    for item in items:
        item_type = item.get('type', 'unknown')
        resource_types[item_type] = resource_types.get(item_type, 0) + 1
        
        # Verificar NSGs con múltiples subnets
        if item_type == 'Microsoft.Network/networkSecurityGroups':
            subnets = item.get('properties', {}).get('subnets', [])
            if len(subnets) > 1:
                nsgs_multi_subnet.append({
                    'name': item['name'],
                    'subnet_count': len(subnets),
                    'subnets': [s['id'].split('/')[-1] for s in subnets]
                })
        
        # Verificar Route Tables con múltiples subnets
        elif item_type == 'Microsoft.Network/routeTables':
            subnets = item.get('properties', {}).get('subnets', [])
            if len(subnets) > 1:
                route_tables_multi_subnet.append({
                    'name': item['name'],
                    'subnet_count': len(subnets),
                    'subnets': [s['id'].split('/')[-1] for s in subnets]
                })
    
    print(f"  - Tipos de recursos: {len(resource_types)}")
    for res_type, count in sorted(resource_types.items()):
        print(f"    • {res_type}: {count}")
    
    print(f"\n🔒 NSGs con múltiples subnets: {len(nsgs_multi_subnet)}")
    for nsg in nsgs_multi_subnet:
        print(f"  • {nsg['name']}: {nsg['subnet_count']} subnets → {', '.join(nsg['subnets'])}")
    
    print(f"\n🛣️ Route Tables con múltiples subnets: {len(route_tables_multi_subnet)}")
    for rt in route_tables_multi_subnet:
        print(f"  • {rt['name']}: {rt['subnet_count']} subnets → {', '.join(rt['subnets'])}")
    
    # Generar diagramas en diferentes modos
    modes = [
        ('network', 'Diagrama de Red (con NSGs y Route Tables duplicados)'),
        ('infrastructure', 'Diagrama de Infraestructura (jerárquico)'),
        ('components', 'Diagrama de Componentes (por tipo)'),
        ('all', 'Diagrama Multi-página (todos los modos)')
    ]
    
    for mode, description in modes:
        print(f"\n🎨 Generando: {description}")
        
        try:
            xml_content = generate_drawio_file(
                items, 
                dependencies, 
                embed_data=True, 
                diagram_mode=mode
            )
            
            output_file = f"demo_diagram_{mode}.drawio"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            print(f"✅ Guardado: {output_file}")
            
            # Estadísticas del diagrama generado
            nsg_count = xml_content.count('demo-nsg-web-tier') + xml_content.count('demo-nsg-data-tier') + xml_content.count('demo-nsg-management')
            rt_count = xml_content.count('demo-rt-shared') + xml_content.count('demo-rt-secure')
            
            if mode == 'network':
                print(f"   📍 NSGs aparecen: {nsg_count} veces (deberían aparecer múltiples veces)")
                print(f"   📍 Route Tables aparecen: {rt_count} veces (deberían aparecer múltiples veces)")
            
        except Exception as e:
            print(f"❌ Error generando {mode}: {e}")

def main():
    print("🚀 Generador de Diagramas de Demostración")
    print("=" * 50)
    
    try:
        generate_demo_diagrams()
        
        print("\n🎉 ¡Generación completada!")
        print("\n📁 Archivos generados:")
        print("  • demo_diagram_network.drawio     - Vista de red con elementos duplicados")
        print("  • demo_diagram_infrastructure.drawio - Vista jerárquica tradicional")
        print("  • demo_diagram_components.drawio  - Vista por componentes")
        print("  • demo_diagram_all.drawio         - Todas las vistas en páginas separadas")
        
        print("\n💡 Para ver los resultados:")
        print("  1. Abre cualquier archivo .drawio en https://app.diagrams.net")
        print("  2. En el modo 'network', verás NSGs y Route Tables duplicados en sus subnets correspondientes")
        print("  3. En el modo 'all', tendrás 4 páginas diferentes para explorar")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

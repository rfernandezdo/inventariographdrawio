#!/usr/bin/env python3
"""
Test del modo network con datos reales enmascarados
"""

import sys
import os
import json
# Agregar el directorio padre al path para importar src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from src.drawio_export import generate_drawio_file
    print("✅ Importación exitosa")
    
    # Cargar datos enmascarados
    data_file = '../data/masked_realistic_inventory.json'
    if os.path.exists(data_file):
        print(f"📂 Cargando datos desde: {data_file}")
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        items = data.get('items', [])
        print(f"📊 Recursos cargados: {len(items)}")
        
        # Filtrar solo recursos de red para este test
        network_items = []
        for item in items:
            resource_type = (item.get('type') or '').lower()
            if any(net_type in resource_type for net_type in [
                'network/', 'compute/virtualmachines', 'management/', 'keyvault', 'resources/'
            ]):
                network_items.append(item)
        
        print(f"🌐 Recursos de red filtrados: {len(network_items)}")
        
        if network_items:
            print("🔥 Generando diagrama de red con datos reales...")
            content = generate_drawio_file(
                network_items[:50],  # Limitar a 50 recursos para test
                [],  # No dependencies for this test
                embed_data=False,
                include_ids=None,
                diagram_mode='network'
            )
            
            output_file = './fixtures/test-network-real-data.drawio'
            with open(output_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Archivo generado: {output_file}")
            print(f"📊 Tamaño: {len(content):,} caracteres")
            
        else:
            print("⚠️ No se encontraron recursos de red en los datos")
    else:
        print(f"❌ No se encontró el archivo de datos: {data_file}")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

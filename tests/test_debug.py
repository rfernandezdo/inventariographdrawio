#!/usr/bin/env python3
"""
Test básico para depurar problemas
"""

import sys
import os
import json

def test_basic():
    """Test básico de funcionamiento."""
    print("✅ Test básico iniciado")
    
    # Verificar que el archivo de datos enmascarados existe
    masked_file = '../data/masked_realistic_inventory.json'
    
    if os.path.exists(masked_file):
        print(f"✅ Archivo de datos enmascarados encontrado: {masked_file}")
        try:
            with open(masked_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ Datos cargados correctamente: {len(data.get('items', []))} items")
            print(f"✅ Metadatos: {data.get('metadata', {})}")
            
            # Mostrar algunos tipos de recursos
            types = {}
            for item in data.get('items', []):
                item_type = item.get('type', 'unknown')
                types[item_type] = types.get(item_type, 0) + 1
            
            print("✅ Tipos de recursos encontrados:")
            for res_type, count in types.items():
                print(f"   - {res_type}: {count}")
                
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return False
            
    else:
        print(f"❌ No se encontró el archivo: {masked_file}")
        return False
    
    return True

if __name__ == '__main__':
    print("🔧 DEPURACIÓN DEL SISTEMA DE CACHE")
    print("=" * 50)
    
    success = test_basic()
    
    if success:
        print("\n✅ Test básico completado exitosamente")
    else:
        print("\n❌ Test básico falló")
        sys.exit(1)

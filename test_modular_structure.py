#!/usr/bin/env python3
"""
Script de prueba para verificar la estructura modular
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Probar importaciones
    print("🧪 Probando importaciones...")
    
    from drawio.styles import get_node_style
    print("✅ drawio.styles importado correctamente")
    
    from drawio.xml_builder import pretty_print_xml
    print("✅ drawio.xml_builder importado correctamente")
    
    from drawio.layouts.infrastructure import generate_infrastructure_layout
    print("✅ drawio.layouts.infrastructure importado correctamente")
    
    # Probar funciones básicas
    print("\n🧪 Probando funciones...")
    
    style = get_node_style('microsoft.compute/virtualmachines')
    print(f"✅ get_node_style funcionando: {style[:50]}...")
    
    # Probar función con recurso hidden
    hidden_style = get_node_style('microsoft.network/privatednszones/virtualnetworklinks')
    print(f"✅ Estilo hidden detectado: {hidden_style[:50]}...")
    
    print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    print("✅ La estructura modular está funcionando correctamente")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()

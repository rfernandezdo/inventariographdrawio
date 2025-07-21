#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Probando importación de icons...")
try:
    from drawio.icons import AZURE_ICONS, HIDDEN_RESOURCE_TYPES
    print(f"✅ Icons importado: {len(AZURE_ICONS)} iconos cargados")
except Exception as e:
    print(f"❌ Error en icons: {e}")

print("\nProbando importación de styles...")
try:
    from drawio.styles import get_node_style
    print("✅ Styles importado correctamente")
    style = get_node_style('microsoft.compute/virtualmachines')
    print(f"✅ Función funciona: {style[:30]}...")
except Exception as e:
    print(f"❌ Error en styles: {e}")
    import traceback
    traceback.print_exc()

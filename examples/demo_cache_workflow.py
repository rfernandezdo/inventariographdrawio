#!/usr/bin/env python3
"""
demo_cache_workflow.py

Demuestra el flujo de trabajo con cache local y procesamiento posterior.
"""

import sys
import os
import subprocess
from datetime import datetime

def run_command(cmd, description):
    """Ejecuta un comando y muestra el resultado."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"💻 Comando: {cmd}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=False)
    return result.returncode == 0

def main():
    print("🚀 DEMO: Flujo de trabajo con cache local")
    print("=" * 60)
    
    # 1. Consulta inicial con cache
    print("\n1️⃣ PASO 1: Primera consulta (creará cache)")
    success = run_command(
        "python3 ../src/cli.py --diagram-mode infrastructure --export-json inventario_$(date +%Y%m%d).json",
        "Consultar Azure y crear cache + exportar JSON"
    )
    
    if not success:
        print("❌ Error en la primera consulta")
        return
    
    # 2. Segunda consulta usando cache
    print("\n2️⃣ PASO 2: Segunda consulta (usará cache)")
    run_command(
        "python3 ../src/cli.py --diagram-mode network",
        "Generar diagrama de red usando cache (mucho más rápido)"
    )
    
    # 3. Usar datos exportados sin consultar Azure
    print("\n3️⃣ PASO 3: Procesamiento posterior sin Azure")
    
    # Buscar el archivo JSON más reciente
    import glob
    json_files = glob.glob("inventario_*.json")
    if json_files:
        latest_json = max(json_files, key=os.path.getctime)
        run_command(
            f"python3 ../src/cli.py --input-json {latest_json} --diagram-mode components --output componentes_offline.drawio",
            "Generar diagrama de componentes desde JSON (sin consultar Azure)"
        )
    
    # 4. Mostrar información del cache
    print("\n4️⃣ PASO 4: Información del cache")
    run_command(
        "ls -la .azure_cache/",
        "Ver archivos de cache creados"
    )
    
    # 5. Limpiar cache
    print("\n5️⃣ PASO 5: Gestión del cache")
    run_command(
        "python3 ../src/cli.py --clear-cache",
        "Limpiar cache local"
    )
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETADO")
    print("\n📋 Resumen de archivos generados:")
    print("   - azure_full_hierarchy_with_icons.drawio (infraestructura)")
    print("   - azure_full_hierarchy_with_icons.drawio (red, sobrescrito)")
    print("   - componentes_offline.drawio (componentes)")
    print(f"   - inventario_*.json (datos exportados)")
    
    print("\n💡 Casos de uso del cache:")
    print("   ✅ Desarrollo/testing: evitar consultas repetidas")
    print("   ✅ Presentaciones: datos consistentes")
    print("   ✅ Análisis offline: sin dependencia de Azure")
    print("   ✅ CI/CD: generar múltiples diagramas desde un snapshot")

if __name__ == '__main__':
    main()

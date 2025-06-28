#!/usr/bin/env python3
"""
test_cache_system.py

Script para probar el sistema de cache con datos de prueba simulados.
"""

import sys
import os
import json
import tempfile
from datetime import datetime

# Añadir src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def create_test_json():
    """Crea un archivo JSON de prueba usando datos enmascarados realistas."""
    # Intentar cargar datos enmascarados realistas
    masked_file = '../data/masked_realistic_inventory.json'
    
    if os.path.exists(masked_file):
        print(f"📂 Usando datos enmascarados realistas: {masked_file}")
        try:
            with open(masked_file, 'r', encoding='utf-8') as f:
                masked_data = json.load(f)
            
            print(f"✅ Cargados {len(masked_data['items'])} recursos enmascarados realistas")
            return masked_data
            
        except Exception as e:
            print(f"❌ Error cargando datos enmascarados: {e}")
            print("🔄 Usando datos simulados como fallback")
    else:
        print("📝 Archivo de datos enmascarados no encontrado")
        print("💡 Ejecuta: python3 analyze_cache_and_create_masked_data.py")
        print("🔄 Usando datos simulados como fallback")
    
    # Fallback a datos simulados básicos
    print("📝 Usando datos simulados básicos")
    test_data = {
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "source": "simulated_basic_data",
            "total_items": 8,
            "total_dependencies": 3
        },
        "items": [
            {
                "id": "/subscriptions/test-subscription",
                "name": "Test Subscription",
                "type": "Microsoft.Resources/subscriptions"
            },
            {
                "id": "/subscriptions/test-subscription/resourceGroups/rg-network",
                "name": "rg-network",
                "type": "Microsoft.Resources/subscriptions/resourcegroups",
                "resourceGroup": None,
                "subscriptionId": "test-subscription"
            },
            {
                "id": "/subscriptions/test-subscription/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main",
                "name": "vnet-main",
                "type": "Microsoft.Network/virtualNetworks",
                "resourceGroup": "rg-network",
                "subscriptionId": "test-subscription"
            },
            {
                "id": "/subscriptions/test-subscription/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-web",
                "name": "subnet-web",
                "type": "Microsoft.Network/virtualNetworks/subnets",
                "resourceGroup": "rg-network",
                "subscriptionId": "test-subscription",
                "vnetId": "/subscriptions/test-subscription/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main"
            },
            {
                "id": "/subscriptions/test-subscription/resourceGroups/rg-network/providers/Microsoft.Compute/virtualMachines/vm-web",
                "name": "vm-web",
                "type": "Microsoft.Compute/virtualMachines",
                "resourceGroup": "rg-network",
                "subscriptionId": "test-subscription"
            },
            {
                "id": "/subscriptions/test-subscription/resourceGroups/rg-network/providers/Microsoft.Network/publicIPAddresses/pip-vm",
                "name": "pip-vm",
                "type": "Microsoft.Network/publicIPAddresses",
                "resourceGroup": "rg-network",
                "subscriptionId": "test-subscription"
            },
            {
                "id": "/subscriptions/test-subscription/resourceGroups/rg-network/providers/Microsoft.Network/networkSecurityGroups/nsg-web",
                "name": "nsg-web",
                "type": "Microsoft.Network/networkSecurityGroups",
                "resourceGroup": "rg-network",
                "subscriptionId": "test-subscription"
            },
            {
                "id": "/subscriptions/test-subscription/resourceGroups/rg-network/providers/Microsoft.Storage/storageAccounts/stgtest",
                "name": "stgtest",
                "type": "Microsoft.Storage/storageAccounts",
                "resourceGroup": "rg-network",
                "subscriptionId": "test-subscription"
            }
        ],
        "dependencies": [
            ["/subscriptions/test-subscription", "/subscriptions/test-subscription/resourceGroups/rg-network"],
            ["/subscriptions/test-subscription/resourceGroups/rg-network", "/subscriptions/test-subscription/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main"],
            ["/subscriptions/test-subscription/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main", "/subscriptions/test-subscription/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-main/subnets/subnet-web"]
        ]
    }
    
    return test_data

def test_cache_workflow():
    """Prueba el flujo completo del cache."""
    print("🧪 PROBANDO SISTEMA DE CACHE")
    print("=" * 50)
    
    # 1. Crear archivo JSON de prueba
    test_data = create_test_json()
    test_file = "test_inventory.json"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"✅ Archivo de prueba creado: {test_file}")
    
    # 2. Importar azure_api para probar funciones
    try:
        from src.azure_api import load_from_json_export
        from src.drawio_export import generate_drawio_file
        
        # 3. Cargar datos desde JSON
        print("\n📖 Cargando datos desde JSON...")
        items, dependencies = load_from_json_export(test_file)
        
        if not items:
            print("❌ Error cargando datos")
            return False
        
        print(f"✅ Cargados {len(items)} recursos y {len(dependencies)} dependencias")
        
        # 4. Generar diagramas en todos los modos
        modes = ['infrastructure', 'components', 'network']
        
        for mode in modes:
            print(f"\n🎨 Generando diagrama '{mode}'...")
            try:
                content = generate_drawio_file(
                    items=items,
                    dependencies=dependencies,
                    embed_data=False,
                    include_ids=None,
                    diagram_mode=mode
                )
                
                output_file = f"test_cache_{mode}.drawio"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Generado: {output_file} ({len(content)} caracteres)")
                
            except Exception as e:
                print(f"❌ Error generando {mode}: {e}")
                return False
        
        # 5. Limpiar archivos de prueba
        os.remove(test_file)
        for mode in modes:
            test_file_path = f"test_cache_{mode}.drawio"
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
        
        print("\n🧹 Archivos de prueba eliminados")
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def show_cache_commands():
    """Muestra ejemplos de comandos con cache."""
    print("\n📋 COMANDOS DISPONIBLES CON CACHE:")
    print("=" * 50)
    
    commands = [
        ("Generar con cache automático", "python3 src/cli.py --diagram-mode network"),
        ("Forzar actualización", "python3 src/cli.py --force-refresh"),
        ("Exportar a JSON", "python3 src/cli.py --export-json mi_datos.json"),
        ("Usar desde JSON", "python3 src/cli.py --input-json mi_datos.json --diagram-mode components"),
        ("Sin cache", "python3 src/cli.py --no-cache --diagram-mode infrastructure"),
        ("Limpiar cache", "python3 src/cli.py --clear-cache"),
        ("Archivo personalizado", "python3 src/cli.py --input-json datos.json --output mi_diagrama.drawio")
    ]
    
    for description, command in commands:
        print(f"\n🔧 {description}:")
        print(f"   {command}")
    
    print(f"\n💡 CASOS DE USO:")
    print("   📊 Desarrollo: usar cache para iteraciones rápidas")
    print("   📋 Documentación: exportar snapshot para presentaciones")
    print("   🚀 CI/CD: un snapshot, múltiples diagramas")
    print("   ✈️  Offline: trabajar sin conexión a Azure")

if __name__ == '__main__':
    success = test_cache_workflow()
    show_cache_commands()
    
    if success:
        print(f"\n✅ Sistema de cache funcionando correctamente")
        sys.exit(0)
    else:
        print(f"\n❌ Hay problemas con el sistema de cache")
        sys.exit(1)

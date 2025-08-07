#!/bin/bash

# Script para probar la funcionalidad de la action localmente
# Útil para debugging antes de ejecutar en GitHub Actions

echo "=== Test Local de Azure Infrastructure Diagram Generator ==="
echo "Este script simula la ejecución de la GitHub Action localmente"
echo ""

# Verificar prerequisitos
echo "1. Verificando prerequisitos..."

# Python
if ! command -v python &> /dev/null; then
    echo "ERROR: Python no está instalado"
    exit 1
fi
echo "✓ Python: $(python --version)"

# Azure CLI
if ! command -v az &> /dev/null; then
    echo "ERROR: Azure CLI no está instalado"
    exit 1
fi
echo "✓ Azure CLI: $(az version --output tsv --query '"azure-cli"' 2>/dev/null || echo 'Version no disponible')"

# Login status
echo ""
echo "2. Verificando autenticación de Azure..."
if ! az account show > /dev/null 2>&1; then
    echo "ERROR: No estás autenticado en Azure CLI"
    echo "Por favor ejecuta: az login"
    exit 1
fi

ACCOUNT_INFO=$(az account show --output json 2>/dev/null)
USER_NAME=$(echo "$ACCOUNT_INFO" | python -c "import sys, json; print(json.load(sys.stdin)['user']['name'])" 2>/dev/null || echo "Usuario desconocido")
SUBSCRIPTION_NAME=$(echo "$ACCOUNT_INFO" | python -c "import sys, json; print(json.load(sys.stdin)['name'])" 2>/dev/null || echo "Suscripción desconocida")

echo "✓ Autenticado como: $USER_NAME"
echo "✓ Suscripción activa: $SUBSCRIPTION_NAME"

# Resource Graph extension
echo ""
echo "3. Verificando extensión resource-graph..."
if ! az extension list --output tsv --query "[?name=='resource-graph'].name" | grep -q resource-graph; then
    echo "ADVERTENCIA: Extensión resource-graph no está instalada"
    echo "Instalando..."
    az extension add --name resource-graph --yes
    echo "✓ Extensión resource-graph instalada"
else
    echo "✓ Extensión resource-graph ya está instalada"
fi

# Dependencies
echo ""
echo "4. Verificando dependencias de Python..."
if ! python -c "import requests" 2>/dev/null; then
    echo "ADVERTENCIA: Módulo requests no está instalado"
    echo "Instalando..."
    pip install requests
    echo "✓ Módulo requests instalado"
else
    echo "✓ Módulo requests disponible"
fi

# Test basic functionality
echo ""
echo "5. Ejecutando test básico..."
echo "Comando: python src/cli.py --list-tenants"
echo ""

if python src/cli.py --list-tenants; then
    echo ""
    echo "✓ Test básico exitoso"
else
    echo ""
    echo "✗ Test básico falló"
    exit 1
fi

# Optional: Run with specific parameters
echo ""
echo "6. ¿Quieres ejecutar un test completo? (genera diagrama)"
echo "Ejemplo: python src/cli.py --output test-diagram.drawio --no-embed-data"
echo ""
read -p "¿Ejecutar test completo? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Ejecutando test completo..."
    echo "Comando: python src/cli.py --output test-diagram.drawio --no-embed-data"
    echo ""
    
    if python src/cli.py --output test-diagram.drawio --no-embed-data; then
        echo ""
        echo "✓ Test completo exitoso"
        echo "✓ Archivo generado: test-diagram.drawio"
        echo ""
        echo "Para verificar el resultado:"
        echo "1. Abre https://app.diagrams.net"
        echo "2. Carga el archivo test-diagram.drawio"
    else
        echo ""
        echo "✗ Test completo falló"
        exit 1
    fi
fi

echo ""
echo "=== RESUMEN ==="
echo "✓ Todos los prerequisitos están disponibles"
echo "✓ La funcionalidad básica funciona correctamente"
echo ""
echo "La GitHub Action debería funcionar correctamente con estos mismos parámetros."
echo "Si hay problemas en GitHub Actions, revisa:"
echo "1. Que el service principal tenga permisos de Reader"
echo "2. Que los resource groups/suscripciones especificados existan"
echo "3. Que los IDs en --include-ids sean válidos"

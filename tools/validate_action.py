#!/usr/bin/env python3
"""
Validador de configuración para Azure Infrastructure Diagrams GitHub Action.
Este script verifica que todos los componentes estén correctamente configurados.
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Verificar que un archivo existe"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def check_action_yml():
    """Verificar el archivo action.yml"""
    action_file = "action.yml"
    if not check_file_exists(action_file, "Action metadata"):
        return False
    
    try:
        with open(action_file, 'r') as f:
            action_config = yaml.safe_load(f)
        
        # Verificar campos requeridos
        required_fields = ['name', 'description', 'inputs', 'outputs', 'runs']
        for field in required_fields:
            if field in action_config:
                print(f"✅ Action.yml has required field: {field}")
            else:
                print(f"❌ Action.yml missing required field: {field}")
                return False
        
        # Verificar inputs requeridos
        inputs = action_config.get('inputs', {})
        if 'azure-credentials' in inputs and inputs['azure-credentials'].get('required'):
            print("✅ Azure credentials input is properly configured")
        else:
            print("❌ Azure credentials input not properly configured")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error parsing action.yml: {e}")
        return False

def check_source_files():
    """Verificar archivos fuente principales"""
    source_files = [
        ("src/cli.py", "Main CLI script"),
        ("src/azure_api.py", "Azure API integration"),
        ("src/drawio_export.py", "Draw.io export functionality"),
        ("src/utils.py", "Utility functions")
    ]
    
    all_exist = True
    for file_path, description in source_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_documentation():
    """Verificar documentación"""
    docs = [
        ("README.md", "Main README"),
        ("ACTION_README.md", "GitHub Action README"),
        ("SETUP_GITHUB_ACTION.md", "Setup guide"),
        ("EXAMPLES.md", "Usage examples"),
        ("CHANGELOG.md", "Changelog"),
        ("LICENSE", "License file")
    ]
    
    all_exist = True
    for file_path, description in docs:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_workflow_examples():
    """Verificar ejemplos de workflows"""
    workflow_dir = ".github/workflows"
    if not os.path.exists(workflow_dir):
        print(f"❌ Workflow examples directory not found: {workflow_dir}")
        return False
    
    workflows = []
    for file in os.listdir(workflow_dir):
        if file.endswith('.yml') or file.endswith('.yaml'):
            workflows.append(file)
    
    if workflows:
        print(f"✅ Found {len(workflows)} workflow examples:")
        for workflow in workflows:
            print(f"   - {workflow}")
        return True
    else:
        print("❌ No workflow examples found")
        return False

def check_python_syntax():
    """Verificar sintaxis de Python en archivos fuente"""
    python_files = [
        "src/cli.py",
        "src/azure_api.py", 
        "src/drawio_export.py",
        "src/utils.py",
        "generate_infrastructure_report.py"
    ]
    
    all_valid = True
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                result = subprocess.run([sys.executable, '-m', 'py_compile', file_path], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Python syntax valid: {file_path}")
                else:
                    print(f"❌ Python syntax error in {file_path}: {result.stderr}")
                    all_valid = False
            except Exception as e:
                print(f"❌ Error checking Python syntax for {file_path}: {e}")
                all_valid = False
    
    return all_valid

def check_yaml_syntax():
    """Verificar sintaxis YAML en workflows"""
    workflow_dir = ".github/workflows"
    if not os.path.exists(workflow_dir):
        return True
    
    all_valid = True
    for file in os.listdir(workflow_dir):
        if file.endswith('.yml') or file.endswith('.yaml'):
            file_path = os.path.join(workflow_dir, file)
            try:
                with open(file_path, 'r') as f:
                    yaml.safe_load(f)
                print(f"✅ YAML syntax valid: {file}")
            except yaml.YAMLError as e:
                print(f"❌ YAML syntax error in {file}: {e}")
                all_valid = False
            except Exception as e:
                print(f"❌ Error checking YAML syntax for {file}: {e}")
                all_valid = False
    
    return all_valid

def check_action_branding():
    """Verificar configuración de branding para marketplace"""
    action_file = "action.yml"
    if not os.path.exists(action_file):
        return False
    
    try:
        with open(action_file, 'r') as f:
            action_config = yaml.safe_load(f)
        
        branding = action_config.get('branding', {})
        if 'icon' in branding and 'color' in branding:
            print(f"✅ Branding configured: icon={branding['icon']}, color={branding['color']}")
            return True
        else:
            print("❌ Branding not properly configured for marketplace")
            return False
    except Exception as e:
        print(f"❌ Error checking branding: {e}")
        return False

def check_marketplace_readiness():
    """Verificar preparación para marketplace"""
    print("\n🏪 MARKETPLACE READINESS CHECK")
    print("=" * 50)
    
    checks = [
        ("Action metadata", check_action_yml),
        ("Branding configuration", check_action_branding),
        ("Documentation completeness", check_documentation),
        ("Workflow examples", check_workflow_examples)
    ]
    
    all_ready = True
    for description, check_func in checks:
        if check_func():
            print(f"✅ {description}: READY")
        else:
            print(f"❌ {description}: NOT READY")
            all_ready = False
    
    return all_ready

def main():
    """Función principal"""
    print("🔍 AZURE INFRASTRUCTURE DIAGRAMS - GITHUB ACTION VALIDATOR")
    print("=" * 65)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("action.yml"):
        print("❌ Error: action.yml not found. Please run this script from the repository root.")
        sys.exit(1)
    
    # Lista de verificaciones
    checks = [
        ("Action Configuration", check_action_yml),
        ("Source Files", check_source_files),
        ("Documentation", check_documentation),
        ("Workflow Examples", check_workflow_examples),
        ("Python Syntax", check_python_syntax),
        ("YAML Syntax", check_yaml_syntax)
    ]
    
    print("\n📋 BASIC CHECKS")
    print("=" * 30)
    
    all_passed = True
    for description, check_func in checks:
        print(f"\n{description}:")
        if check_func():
            print(f"✅ {description}: PASSED")
        else:
            print(f"❌ {description}: FAILED")
            all_passed = False
    
    # Verificación de preparación para marketplace
    marketplace_ready = check_marketplace_readiness()
    
    # Resumen final
    print("\n" + "=" * 65)
    print("📊 SUMMARY")
    print("=" * 65)
    
    if all_passed:
        print("✅ All basic checks PASSED")
    else:
        print("❌ Some basic checks FAILED")
    
    if marketplace_ready:
        print("✅ Marketplace readiness: READY")
    else:
        print("❌ Marketplace readiness: NOT READY")
    
    if all_passed and marketplace_ready:
        print("\n🎉 CONGRATULATIONS! The GitHub Action is ready for publication.")
        print("\n📋 Next steps:")
        print("1. Create a new release/tag (e.g., v1.0.0)")
        print("2. Push the tag to trigger marketplace publication")
        print("3. Update the marketplace listing with proper description")
        print("4. Test the action in a real workflow")
        
        return 0
    else:
        print("\n🔧 Please fix the issues above before publishing to marketplace.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

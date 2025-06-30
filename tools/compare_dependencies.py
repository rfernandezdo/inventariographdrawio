#!/usr/bin/env python3
"""
Script para comparar las dependencias entre el modo network normal 
y el modo network con --no-hierarchy-edges
"""
import json
import sys
import os
sys.path.append('src')
from azure_api import find_dependencies

def load_inventory():
    """Cargar el inventario desde el cache"""
    cache_file = '.azure_cache/final_inventory_20250630_17.json'
    if not os.path.exists(cache_file):
        print(f"❌ Error: No se encontró {cache_file}")
        return None
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_dependencies_for_no_hierarchy(dependencies):
    """
    Aplicar el mismo filtrado que se usa en drawio_export.py
    cuando se activa --no-hierarchy-edges
    """
    # Función local para normalizar IDs (como se hace en drawio_export.py)
    def normalize_azure_id(azure_id):
        return azure_id.lower()
    
    HIERARCHICAL_NETWORK_TYPES = [
        'microsoft.network/privateendpoints',
        'microsoft.network/networkinterfaces', 
        'microsoft.network/privatednszones/virtualnetworklinks'
    ]
    
    edges_to_create = []
    
    for src_id, tgt_id in dependencies:
        # Normalizar IDs
        src_id_norm = normalize_azure_id(src_id)
        tgt_id_norm = normalize_azure_id(tgt_id)
        
        # Obtener tipos de recursos
        source_type = None
        target_type = None
        
        # Extraer tipo del ID
        src_parts = src_id_norm.split('/providers/')
        if len(src_parts) > 1:
            provider_part = src_parts[1]
            if '/' in provider_part:
                source_type = '/'.join(provider_part.split('/')[:2]).lower()
        
        tgt_parts = tgt_id_norm.split('/providers/')
        if len(tgt_parts) > 1:
            provider_part = tgt_parts[1]
            if '/' in provider_part:
                target_type = '/'.join(provider_part.split('/')[:2]).lower()
        
        # Verificar si involucra Resource Groups
        has_rg_involvement = (
            'resourcegroups' in src_id_norm.lower() and '/providers/' not in src_id_norm or
            'resourcegroups' in tgt_id_norm.lower() and '/providers/' not in tgt_id_norm
        )
        
        # Verificar si es un enlace VNet-Subnet directo
        is_vnet_subnet_link = (
            source_type == 'microsoft.network/virtualnetworks' and 
            target_type == 'microsoft.network/virtualnetworks/subnets'
        )
        
        # Filtrar dependencias jerárquicas de red específicas
        is_hierarchical_network_dependency = False
        if source_type in HIERARCHICAL_NETWORK_TYPES:
            # Filtrar solo si el target es VNet o Subnet
            if target_type in ['microsoft.network/virtualnetworks', 'microsoft.network/virtualnetworks/subnets']:
                is_hierarchical_network_dependency = True
        elif target_type in HIERARCHICAL_NETWORK_TYPES:
            # Filtrar solo si el source es VNet o Subnet  
            if source_type in ['microsoft.network/virtualnetworks', 'microsoft.network/virtualnetworks/subnets']:
                is_hierarchical_network_dependency = True
        
        # Conservar el enlace si no es jerárquico
        if not has_rg_involvement and not is_vnet_subnet_link and not is_hierarchical_network_dependency:
            edges_to_create.append((src_id, tgt_id))
    
    return edges_to_create

def analyze_dependencies(inventory):
    """Analizar y comparar dependencias"""
    
    print("🔍 Extrayendo todas las dependencias...")
    all_dependencies = find_dependencies(inventory['data'])
    print(f"📊 Total de dependencias encontradas: {len(all_dependencies)}")
    
    print("\n🚫 Aplicando filtros de --no-hierarchy-edges...")
    filtered_dependencies = filter_dependencies_for_no_hierarchy(all_dependencies)
    print(f"📊 Dependencias tras filtrado: {len(filtered_dependencies)}")
    
    # Encontrar dependencias que se eliminaron
    all_deps_set = set(all_dependencies)
    filtered_deps_set = set(filtered_dependencies)
    removed_dependencies = all_deps_set - filtered_deps_set
    
    print(f"\n❌ Dependencias eliminadas: {len(removed_dependencies)}")
    
    # Analizar dependencias eliminadas que NO involucran subnets o vnets
    print("\n🔍 Analizando dependencias eliminadas que NO involucran VNets/Subnets:")
    print("=" * 80)
    
    non_network_removed = []
    
    for src_id, tgt_id in removed_dependencies:
        # Verificar si involucra VNets o Subnets
        involves_vnet_subnet = (
            '/virtualnetworks/' in src_id.lower() or 
            '/virtualnetworks/' in tgt_id.lower() or
            '/subnets/' in src_id.lower() or
            '/subnets/' in tgt_id.lower()
        )
        
        if not involves_vnet_subnet:
            non_network_removed.append((src_id, tgt_id))
            src_name = src_id.split('/')[-1]
            tgt_name = tgt_id.split('/')[-1]
            
            # Extraer tipos
            src_type = "desconocido"
            tgt_type = "desconocido"
            
            if '/providers/' in src_id:
                src_parts = src_id.split('/providers/')[1].split('/')
                if len(src_parts) >= 2:
                    src_type = f"{src_parts[0]}/{src_parts[1]}"
            
            if '/providers/' in tgt_id:
                tgt_parts = tgt_id.split('/providers/')[1].split('/')
                if len(tgt_parts) >= 2:
                    tgt_type = f"{tgt_parts[0]}/{tgt_parts[1]}"
            
            print(f"🔗 {src_name} ({src_type})")
            print(f"   → {tgt_name} ({tgt_type})")
            print(f"   📍 Source: {src_id}")
            print(f"   📍 Target: {tgt_id}")
            print("   " + "-" * 60)
    
    print(f"\n💡 RESUMEN:")
    print(f"   Total eliminadas: {len(removed_dependencies)}")
    print(f"   Eliminadas SIN VNet/Subnet: {len(non_network_removed)}")
    print(f"   Eliminadas CON VNet/Subnet: {len(removed_dependencies) - len(non_network_removed)}")
    
    if non_network_removed:
        print(f"\n⚠️  DEPENDENCIAS POSIBLEMENTE PERDIDAS POR ERROR:")
        print("   Estas dependencias no involucran VNets/Subnets pero fueron eliminadas:")
        for src_id, tgt_id in non_network_removed:
            src_name = src_id.split('/')[-1] 
            tgt_name = tgt_id.split('/')[-1]
            print(f"   • {src_name} → {tgt_name}")

def main():
    print("🔍 COMPARANDO DEPENDENCIAS: Normal vs --no-hierarchy-edges")
    print("=" * 80)
    
    inventory = load_inventory()
    if not inventory:
        return 1
    
    analyze_dependencies(inventory)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

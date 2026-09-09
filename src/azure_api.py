"""
Funciones para obtener y procesar datos de Azure (management groups, recursos, dependencias).
Incluye funcionalidad de cache local para evitar repetir consultas costosas.
"""

import os
import sys
import json
import subprocess
import platform
from datetime import datetime, timedelta
from pathlib import Path

# Detectar si estamos en Windows para subprocess
IS_WINDOWS = platform.system() == 'Windows'

def run_az_command(cmd, **kwargs):
    """Ejecuta comando de Azure CLI con configuración apropiada para el sistema operativo."""
    # En Windows, necesitamos shell=True para ejecutar az.cmd
    if IS_WINDOWS:
        kwargs['shell'] = True
        # En Windows, remover encoding explícito y usar errors='replace' para evitar problemas UTF-8
        if 'encoding' in kwargs:
            del kwargs['encoding']
        kwargs.setdefault('errors', 'replace')  # Reemplazar caracteres problemáticos
    else:
        # En Linux/Mac, asegurar que se use UTF-8 si no se especifica
        kwargs.setdefault('encoding', 'utf-8')
    return subprocess.run(cmd, **kwargs)

# Configuración del cache
CACHE_DIR = Path('.azure_cache')
CACHE_EXPIRY_HOURS = 4  # Cache válido por 4 horas por defecto

def ensure_cache_dir():
    """Asegura que el directorio de cache existe."""
    CACHE_DIR.mkdir(exist_ok=True)

def get_cache_path(cache_type):
    """Obtiene la ruta del archivo de cache para un tipo específico."""
    return CACHE_DIR / f"{cache_type}_{datetime.now().strftime('%Y%m%d_%H')}.json"

def get_latest_cache_file(cache_type):
    """Encuentra el archivo de cache más reciente para un tipo específico."""
    pattern = f"{cache_type}_*.json"
    cache_files = list(CACHE_DIR.glob(pattern))
    if not cache_files:
        return None
    return max(cache_files, key=lambda p: p.stat().st_mtime)

def is_cache_valid(cache_file, max_age_hours=CACHE_EXPIRY_HOURS):
    """Verifica si un archivo de cache sigue siendo válido."""
    if not cache_file or not cache_file.exists():
        return False
    
    file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
    return file_age < timedelta(hours=max_age_hours)

def save_to_cache(data, cache_type):
    """Guarda datos en el cache local."""
    ensure_cache_dir()
    cache_file = get_cache_path(cache_type)
    
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'data': data,
        'metadata': {
            'count': len(data) if isinstance(data, list) else 1,
            'cache_type': cache_type
        }
    }
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    print(f"INFO: Datos guardados en cache: {cache_file}")

def load_from_cache(cache_type):
    """Carga datos desde el cache local si existe y es válido."""
    cache_file = get_latest_cache_file(cache_type)
    
    if not is_cache_valid(cache_file):
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        print(f"INFO: Usando cache: {cache_file} (creado: {cache_data.get('timestamp', 'desconocido')})")
        return cache_data['data']
    
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"ADVERTENCIA: Error leyendo cache {cache_file}: {e}")
        return None

def get_current_tenant_id():
    """Obtiene el Tenant ID actual del CLI de Azure."""
    try:
        cmd = ["az", "account", "show", "--query", "tenantId", "-o", "tsv"]
        result = run_az_command(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        tenant_id = result.stdout.strip()
        return tenant_id if tenant_id else None
    except Exception as e:
        print(f"ADVERTENCIA: No se pudo obtener el tenant actual: {e}")
        return None

def check_azure_login():
    """Verifica si el usuario está autenticado en Azure CLI."""
    try:
        cmd = ["az", "account", "show"]
        result = run_az_command(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        account_info = json.loads(result.stdout)
        print(f"INFO: Autenticado como: {account_info.get('user', {}).get('name', 'Usuario desconocido')}")
        print(f"INFO: Suscripción activa: {account_info.get('name', 'Desconocida')} ({account_info.get('id', 'ID desconocido')})")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: No se ha iniciado sesión en Azure CLI.")
        print(f"Por favor ejecuta: az login")
        if e.stderr:
            print(f"Detalles del error: {e.stderr}")
        return False
    except Exception as e:
        print(f"ERROR: Error verificando autenticación de Azure: {e}")
        return False

def list_available_tenants():
    """Lista todos los tenants disponibles desde el CLI de Azure."""
    try:
        cmd = ["az", "account", "list", "--query", "[].{name:name, tenantId:tenantId, subscriptionId:id}", "-o", "json"]
        result = run_az_command(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        tenants = json.loads(result.stdout)
        return tenants
    except Exception as e:
        print(f"ADVERTENCIA: No se pudieron obtener los tenants disponibles: {e}")
        return []

def filter_items_by_tenant(items, tenant_id):
    """Filtra elementos por tenant ID."""
    if not tenant_id:
        return items
        
    print(f"INFO: Filtrando recursos por tenant: {tenant_id}")
    original_count = len(items)
    
    filtered_items = []
    for item in items:
        item_tenant = item.get('tenantId')
        if item_tenant == tenant_id:
            filtered_items.append(item)
        elif not item_tenant:
            # Si no tiene tenantId, revisar si es un recurso nested (como subnets)
            # que debería heredar el tenant de su padre
            item_type = item.get('type', '').lower()
            if item_type == 'microsoft.network/virtualnetworks/subnets':
                # Para subnets, intentar determinar el tenant desde la VNet padre
                vnet_id = item.get('vnetId', '')
                if vnet_id:
                    # Buscar la VNet en la lista de items
                    vnet_item = next((i for i in items if i.get('id', '').lower() == vnet_id.lower()), None)
                    if vnet_item and vnet_item.get('tenantId') == tenant_id:
                        filtered_items.append(item)
                        continue
            
            # Si no se pudo determinar el tenant, incluir por seguridad
            print(f"ADVERTENCIA: Elemento sin tenantId incluido: {item.get('name', 'N/A')} ({item.get('type', 'N/A')})")
            filtered_items.append(item)
    
    filtered_count = len(filtered_items)
    if filtered_count != original_count:
        print(f"INFO: Filtrado por tenant completado: {original_count} → {filtered_count} elementos")
    
    return filtered_items

def clear_cache(cache_type=None):
    """Limpia el cache. Si cache_type es None, limpia todo."""
    ensure_cache_dir()
    
    if cache_type:
        pattern = f"{cache_type}_*.json"
        files_to_delete = list(CACHE_DIR.glob(pattern))
    else:
        files_to_delete = list(CACHE_DIR.glob("*.json"))
    
    for file in files_to_delete:
        file.unlink()
        print(f"INFO: Cache eliminado: {file}")
    
    if not files_to_delete:
        print("INFO: No hay archivos de cache para eliminar")

def get_azure_management_groups_with_powershell():
    import platform
    if platform.system() != "Windows":
        print("ADVERTENCIA: La obtención de management groups vía PowerShell solo está soportada en Windows con Az PowerShell instalado.")
        return []
    try:
        cmd = [
            "powershell", "-Command",
            "Search-AzGraph -Query \"ResourceContainers | where type =~ 'microsoft.management/managementgroups'\" | ConvertTo-Json -Depth 10"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        data = json.loads(result.stdout)
        if isinstance(data, dict) and 'id' in data:
            return [data]
        elif isinstance(data, list):
            return data
        else:
            return []
    except Exception as e:
        print(f"ADVERTENCIA: No se pudieron obtener management groups vía PowerShell: {e}")
        return []

def get_azure_management_groups(use_cache=True):
    """Obtiene management groups, usando cache si está disponible."""
    if use_cache:
        cached_data = load_from_cache('management_groups')
        if cached_data:
            return cached_data
    
    import platform
    mg_data = []
    
    # Intentar con PowerShell en Windows
    if platform.system() == "Windows":
        mg_data = get_azure_management_groups_with_powershell()
        if mg_data:
            print(f"INFO: Se han encontrado {len(mg_data)} management groups (PowerShell).")
            if use_cache:
                save_to_cache(mg_data, 'management_groups')
            return mg_data
    
    # Fallback a REST API si PowerShell falla o no está en Windows
    try:
        import requests
        token_cmd = ["az", "account", "get-access-token", "--resource", "https://management.azure.com/", "--output", "json"]
        token_result = run_az_command(token_cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        token = json.loads(token_result.stdout)["accessToken"]
        url = "https://management.azure.com/providers/Microsoft.Management/managementGroups?api-version=2021-04-01&$expand=parent"
        headers = {"Authorization": f"Bearer {token}"}
        mg_list = []
        next_link = url
        while next_link:
            resp = requests.get(next_link, headers=headers)
            if resp.status_code != 200:
                print(f"ADVERTENCIA: No se pudieron obtener management groups vía REST API: {resp.status_code} {resp.text}")
                break
            data = resp.json()
            for mg in data.get("value", []):
                mg_obj = {
                    'id': mg.get('id'),
                    'type': mg.get('type', 'microsoft.management/managementgroups'),
                    'name': mg.get('name'),
                    'displayName': mg.get('properties', {}).get('displayName'),
                    'properties': mg.get('properties', {}),
                    'parent': mg.get('properties', {}).get('parent', {}).get('id')
                }
                mg_list.append(mg_obj)
            next_link = data.get("nextLink")
        print(f"INFO: Se han encontrado {len(mg_list)} management groups (REST API).")
        
        if use_cache:
            save_to_cache(mg_list, 'management_groups')
            
        return mg_list
    except Exception as e:
        print(f"ADVERTENCIA: No se pudieron obtener management groups vía REST API: {e}")
        return []

def enrich_management_groups_with_ancestors(mg_list):
    """Enriquece management groups con información de ancestros."""
    if not mg_list:
        return []
    
    for i, mg in enumerate(mg_list):
        mg_name = mg.get('name')
        if not mg_name:
            continue
        try:
            query = ("ResourceContainers | where type =~ 'microsoft.management/managementgroups' "
                     f"| where name == '{mg_name}'")
            cmd = [
                "az", "graph", "query", "-q", query, "--management-groups", mg_name, "--output", "json"
            ]
            result = run_az_command(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
            data = json.loads(result.stdout)
            if data.get('data'):
                mg_full = data['data'][0]
                for k, v in mg_full.items():
                    if k == 'properties' and isinstance(v, dict):
                        mg.setdefault('properties', {})
                        for pk, pv in v.items():
                            mg['properties'][pk] = pv
                    else:
                        mg[k] = v
                ancestors = mg.get('properties', {}).get('details', {}).get('managementGroupAncestorsChain')
                if not ancestors:
                    ancestors = mg_full.get('properties', {}).get('details', {}).get('managementGroupAncestorsChain')
                    if ancestors:
                        mg.setdefault('properties', {}).setdefault('details', {})['managementGroupAncestorsChain'] = ancestors
        except Exception as e:
            print(f"ADVERTENCIA: No se pudo enriquecer el management group {mg_name} con datos completos: {e}")
    return mg_list

def run_az_graph_query_with_pagination(query, use_cache=True, cache_key=None):
    """Ejecuta query de Azure Resource Graph con paginación y cache opcional."""
    if use_cache and cache_key:
        cached_data = load_from_cache(f'graph_query_{cache_key}')
        if cached_data:
            return cached_data
    
    all_results = []
    skip_token = None
    page_count = 0
    
    try:
        while True:
            page_count += 1
            print(f"INFO: Consultando página {page_count} de Resource Graph...")
            
            cmd = ["az", "graph", "query", "-q", query, "--first", "1000", "--output", "json"]
            if skip_token:
                cmd += ["--skip-token", skip_token]
            
            try:
                result = run_az_command(cmd, capture_output=True, text=True, check=True, timeout=120, encoding='utf-8')
                data = json.loads(result.stdout)
                page_results = data.get('data', [])
                all_results.extend(page_results)
                print(f"INFO: Página {page_count}: {len(page_results)} elementos")
                
                skip_token = data.get('skipToken')
                if not skip_token:
                    break
                    
            except subprocess.TimeoutExpired:
                print(f"ERROR: Timeout en la consulta de Resource Graph (página {page_count})")
                raise
            except json.JSONDecodeError as e:
                print(f"ERROR: Respuesta JSON inválida de Azure Resource Graph: {e}")
                print(f"Stdout: {result.stdout[:500]}...")
                raise
            except subprocess.CalledProcessError as e:
                print(f"ERROR: Falló comando az graph query (página {page_count})")
                print(f"Código de salida: {e.returncode}")
                if e.stderr:
                    print(f"Error: {e.stderr}")
                raise
    
    except Exception as e:
        print(f"ERROR: Fallo en consulta de Resource Graph después de {page_count} páginas: {e}")
        raise
    
    print(f"INFO: Consulta completada. Total: {len(all_results)} elementos en {page_count} páginas")
    
    if use_cache and cache_key:
        save_to_cache(all_results, f'graph_query_{cache_key}')
    
    return all_results

def query_specific_resource_ids(resource_ids):
    """
    Consulta recursos específicos por sus IDs en Azure Resource Graph.
    Esto es útil cuando se necesita obtener recursos que no están en los primeros 1000 resultados.
    """
    if not resource_ids:
        return []
    
    print(f"INFO: Consultando {len(resource_ids)} recursos específicos por ID...")
    
    all_results = []
    # Procesar en lotes de 10 IDs para evitar queries muy largas
    batch_size = 10
    
    for i in range(0, len(resource_ids), batch_size):
        batch = resource_ids[i:i+batch_size]
        
        # Construir query con condiciones OR para cada ID
        conditions = []
        parent_conditions = []
        
        for rid in batch:
            # Limpiar el ID y hacerlo case-insensitive
            clean_id = rid.strip()
            conditions.append(f"id =~ '{clean_id}'")
            
            # Si es un Resource Group, también buscar recursos que pertenezcan a él
            if '/resourcegroups/' in clean_id.lower() and '/providers/' not in clean_id.lower():
                parent_conditions.append(f"id startswith '{clean_id}/'")
        
        # Construir la query completa
        where_clause = " or ".join(conditions)
        query_parts = [
            f"resourcecontainers | where {where_clause}",
            f"resources | where {where_clause}"
        ]
        
        # Agregar búsqueda de recursos hijos si hay Resource Groups
        if parent_conditions:
            parent_where = " or ".join(parent_conditions)
            query_parts.append(f"resources | where {parent_where}")
        
        query = " | union ".join(f"({part})" for part in query_parts)
        
        try:
            cmd = ["az", "graph", "query", "-q", query, "--first", "1000", "--output", "json"]
            result = run_az_command(cmd, capture_output=True, text=True, check=True, timeout=120, encoding='utf-8')
            data = json.loads(result.stdout)
            batch_results = data.get('data', [])
            all_results.extend(batch_results)
            print(f"INFO: Lote {i//batch_size + 1}: {len(batch_results)} recursos encontrados")
        except Exception as e:
            print(f"ADVERTENCIA: Error consultando lote {i//batch_size + 1}: {e}")
            continue
    
    print(f"INFO: Total de recursos específicos obtenidos: {len(all_results)}")
    return all_results

def get_azure_resources(use_cache=True, force_refresh=False, tenant_filter=None, specific_ids=None):
    """Obtiene todos los recursos de Azure con opciones de cache y filtrado por tenant."""
    if force_refresh:
        print("INFO: Forzando actualización, ignorando cache...")
        clear_cache()
    
    # Verificar Azure CLI
    print("INFO: Verificando Azure CLI...")
    if not os.system("az version > " + ("nul" if os.name == 'nt' else "/dev/null 2>&1")) == 0:
        print("\nERROR: Azure CLI no está instalado o no está en el PATH.")
        print("Por favor instala Azure CLI desde: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        sys.exit(1)
    
    # Verificar autenticación
    print("INFO: Verificando autenticación...")
    if not check_azure_login():
        sys.exit(1)
    
    # Información del tenant
    if tenant_filter:
        print(f"INFO: Filtrando recursos por tenant: {tenant_filter}")
    
    print("INFO: Obteniendo management groups (REST API o PowerShell) y recursos con az graph query...")
    
    # Obtener management groups con cache
    try:
        mg_items = get_azure_management_groups(use_cache=use_cache)
        mg_items = enrich_management_groups_with_ancestors(mg_items)
        print(f"INFO: Se encontraron {len(mg_items)} management groups")
    except Exception as e:
        print(f"ERROR: Error obteniendo management groups: {e}")
        raise
    
    try:
        print("INFO: Consultando recursos de Azure...")
        
        # Si se especifican IDs específicos, consultarlos directamente además de la consulta general
        specific_items = []
        if specific_ids:
            specific_items = query_specific_resource_ids(specific_ids)
            if specific_items:
                print(f"INFO: {len(specific_items)} recursos específicos obtenidos por ID")
        
        # Consulta general de todos los recursos
        rest_query = "resourcecontainers | where type != 'microsoft.management/managementgroups' | union resources"
        rest_items = run_az_graph_query_with_pagination(rest_query, use_cache=use_cache, cache_key='all_resources')
        print(f"INFO: Se han encontrado {len(rest_items)} recursos y resource containers (sin management groups).")
        
        # Combinar resultados específicos con los generales, evitando duplicados
        if specific_items:
            existing_ids = {item['id'].lower() for item in rest_items}
            for item in specific_items:
                if item['id'].lower() not in existing_ids:
                    rest_items.append(item)
                    existing_ids.add(item['id'].lower())
            print(f"INFO: Recursos totales después de combinar con específicos: {len(rest_items)}")
        
        # Procesar subnets de VNets
        print("INFO: Procesando subnets de VNets...")
        extra_subnets = []
        for vnet in rest_items:
            if vnet.get('type', '').lower() == 'microsoft.network/virtualnetworks':
                vnet_id = vnet['id']
                subnets = vnet.get('properties', {}).get('subnets', [])
                for subnet in subnets:
                    subnet_id = subnet.get('id')
                    if not subnet_id:
                        subnet_id = vnet_id + "/subnets/" + subnet.get('name', 'unknown')
                    subnet_item = {
                        'id': subnet_id,
                        'name': subnet.get('name', 'unknown'),
                        'type': 'microsoft.network/virtualnetworks/subnets',
                        'properties': subnet,
                        'vnetId': vnet_id,
                        'tenantId': vnet.get('tenantId')  # Heredar tenant de la VNet
                    }
                    extra_subnets.append(subnet_item)
        if extra_subnets:
            print(f"INFO: Se han añadido {len(extra_subnets)} subnets como nodos independientes.")
            
        all_items = mg_items + rest_items + extra_subnets
        print(f"INFO: Total de elementos combinados: {len(all_items)}")
        
        # Aplicar filtrado por tenant si se especifica
        if tenant_filter:
            print(f"INFO: Aplicando filtro por tenant: {tenant_filter}")
            original_count = len(all_items)
            all_items = filter_items_by_tenant(all_items, tenant_filter)
            print(f"INFO: Filtrado completado: {original_count} → {len(all_items)} elementos")
        
        # Guardar combinación final en cache si se está usando cache
        if use_cache:
            cache_suffix = f"_{tenant_filter}" if tenant_filter else ""
            save_to_cache(all_items, f'final_inventory{cache_suffix}')
            
        return all_items
        
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Falló la consulta de Azure Resource Graph.")
        print(f"Código de salida: {e.returncode}")
        if e.stderr:
            print(f"Error stderr: {e.stderr}")
        if e.stdout:
            print(f"Error stdout: {e.stdout}")
        print("\nVerifica:")
        print("1. Que has iniciado sesión: az login")
        print("2. Que tienes permisos de Reader en las suscripciones")
        print("3. Que la extensión resource-graph está instalada: az extension add --name resource-graph")
        raise
    except Exception as e:
        print(f"\nERROR al ejecutar consulta de Azure: {e}")
        print("Asegúrate de haber iniciado sesión ('az login') y tener los permisos necesarios.")
        import traceback
        traceback.print_exc()
        raise

def find_dependencies(all_items):
    print("INFO: Analizando dependencias...")
    dependencies = set()
    item_map = {item['id'].lower(): item for item in all_items}
    all_item_ids = set(item_map.keys())
    managed_identity_ids = set(
        item['id'].lower() for item in all_items
        if item.get('type', '').lower() == 'microsoft.managedidentity/userassignedidentities'
    )
    for item in all_items:
        source_id_lower = item['id'].lower()
        item_type_lower = item.get('type', '').lower()
        parent_id = None
        
        # Handle hierarchical dependencies
        if item_type_lower == 'microsoft.management/managementgroups':
            mg_ancestors = item.get('properties', {}).get('details', {}).get('managementGroupAncestorsChain', [])
            if isinstance(mg_ancestors, list) and len(mg_ancestors) > 0:
                parent_id = mg_ancestors[0].get('id', '').lower()
            else:
                try:
                    parent_id = item['properties']['details']['parent']['id'].lower()
                except (KeyError, TypeError, AttributeError):
                    parent_id = None
        elif item_type_lower == 'microsoft.resources/subscriptions':
            mg_id = None
            mg_chain = item.get('properties', {}).get('managementGroupAncestorsChain')
            if isinstance(mg_chain, list) and len(mg_chain) > 0:
                mg_ancestor = mg_chain[0]
                mg_id_candidate = mg_ancestor.get('id')
                if not mg_id_candidate and mg_ancestor.get('name'):
                    mg_id_candidate = f"/providers/Microsoft.Management/managementGroups/{mg_ancestor['name']}"
                if mg_id_candidate and mg_id_candidate.lower() in all_item_ids:
                    parent_id = mg_id_candidate.lower()
                else:
                    parent_id = None
            else:
                parent_id = None
            if not parent_id:
                print(f"ADVERTENCIA: La suscripción '{item.get('name')}' no se enlazó a ningún management group.")
        elif item_type_lower == 'microsoft.resources/subscriptions/resourcegroups':
            parent_id = f"/subscriptions/{item['subscriptionId']}".lower()
        elif 'resourceGroup' in item and 'subscriptionId' in item:
            parent_id = f"/subscriptions/{item['subscriptionId']}/resourcegroups/{item['resourceGroup']}".lower()
        elif item_type_lower == 'microsoft.network/virtualnetworks/subnets':
            parent_id = item.get('vnetId', '').lower()
        
        if parent_id and parent_id in all_item_ids:
            dependencies.add((source_id_lower, parent_id))
        
        # Detección genérica de sub-recurso anidado bajo otro recurso del inventario
        # (ej. SQL Database -> SQL Server, Event Hub -> Namespace, Blob Service ->
        # Storage Account). Se busca el ID de OTRO item, lo más específico posible,
        # que sea un prefijo de segmento exacto del ID de este item.
        governance_types = {
            'microsoft.management/managementgroups',
            'microsoft.resources/subscriptions',
            'microsoft.resources/subscriptions/resourcegroups',
        }
        if item_type_lower not in governance_types:
            best_container_id = None
            for candidate_id, candidate_item in item_map.items():
                if candidate_id == source_id_lower:
                    continue
                if candidate_item.get('type', '').lower() in governance_types:
                    continue
                if source_id_lower.startswith(candidate_id + '/'):
                    if best_container_id is None or len(candidate_id) > len(best_container_id):
                        best_container_id = candidate_id
            if best_container_id and best_container_id != parent_id:
                dependencies.add((source_id_lower, best_container_id))
        
        # Dependencias específicas basadas en la estructura del ID
        
        # Para virtualnetworklinks, extraer la relación con su privatednszones padre
        if item_type_lower == 'microsoft.network/privatednszones/virtualnetworklinks':
            # ID típico: /subscriptions/.../resourceGroups/.../providers/Microsoft.Network/privateDnsZones/ZONE_NAME/virtualNetworkLinks/LINK_NAME
            # Extraer la parte hasta privateDnsZones/ZONE_NAME
            item_id = item.get('id', '')
            if '/privatednszones/' in item_id.lower() and '/virtualnetworklinks/' in item_id.lower():
                # Encontrar la posición donde termina la zona DNS
                vnet_links_pos = item_id.lower().find('/virtualnetworklinks/')
                if vnet_links_pos > 0:
                    parent_dns_zone_id = item_id[:vnet_links_pos].lower()
                    if parent_dns_zone_id in all_item_ids and parent_dns_zone_id != source_id_lower:
                        dependencies.add((source_id_lower, parent_dns_zone_id))
                        print(f"INFO: Dependencia DNS extraída: {item.get('name', 'N/A')} → {parent_dns_zone_id.split('/')[-1]}")
        
        # Track subnet dependencies for this specific item to avoid VNet redundancy
        subnet_dependencies_added = set()
        
        def scan_properties(props):
            nonlocal subnet_dependencies_added
            
            if isinstance(props, dict):
                for k, value in props.items():
                    if isinstance(value, str) and '/subnets/' in value.lower():
                        subnet_id = value.lower()
                        if subnet_id in all_item_ids and subnet_id != source_id_lower:
                            dependencies.add((source_id_lower, subnet_id))
                            subnet_dependencies_added.add(subnet_id)
                            continue
                    if k.lower() == 'userassignedidentities' and isinstance(value, dict):
                        for mi_id in value.keys():
                            mi_id_lower = mi_id.lower()
                            if mi_id_lower in managed_identity_ids and mi_id_lower != source_id_lower:
                                dependencies.add((source_id_lower, mi_id_lower))
                    scan_properties(value)
            elif isinstance(props, list):
                for element in props: 
                    scan_properties(element)
            elif isinstance(props, str):
                if '/subnets/' in props.lower() and props.lower() in all_item_ids and props.lower() != source_id_lower:
                    dependencies.add((source_id_lower, props.lower()))
                    subnet_dependencies_added.add(props.lower())
                elif props.lower() in all_item_ids and props.lower() != source_id_lower:
                    # Only add VNet dependencies if no subnet dependency exists for this VNet
                    if '/virtualnetworks/' in props.lower() and not '/subnets/' in props.lower():
                        # Check if we already have a subnet dependency from this VNet
                        vnet_id = props.lower()
                        has_subnet_from_this_vnet = any(
                            subnet_id.startswith(vnet_id + '/subnets/') 
                            for subnet_id in subnet_dependencies_added
                        )
                        if not has_subnet_from_this_vnet:
                            dependencies.add((source_id_lower, props.lower()))
                    elif '/virtualnetworks/' not in props.lower():
                        # For non-VNet resources, add dependency normally
                        dependencies.add((source_id_lower, props.lower()))
        
        scan_properties(item)
    print(f"INFO: Se han encontrado {len(dependencies)} relaciones de dependencia.")
    return list(dependencies)

def export_cache_to_json(output_file='azure_inventory_export.json'):
    """Exporta el cache más reciente a un archivo JSON para procesamiento posterior."""
    cache_file = get_latest_cache_file('final_inventory')
    
    if not cache_file or not cache_file.exists():
        print("ERROR: No hay cache de inventario disponible para exportar.")
        print("Ejecuta primero una consulta normal para generar el cache.")
        return False
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        items = cache_data['data']
        dependencies = find_dependencies(items)
        
        export_data = {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'source_cache': str(cache_file),
                'cache_timestamp': cache_data.get('timestamp'),
                'total_items': len(items),
                'total_dependencies': len(dependencies)
            },
            'items': items,
            'dependencies': dependencies
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Inventario exportado a: {output_file}")
        print(f"   📊 {len(items)} recursos, {len(dependencies)} dependencias")
        print(f"   📅 Cache original: {cache_data.get('timestamp', 'desconocido')}")
        return True
        
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"ERROR: No se pudo exportar el cache: {e}")
        return False

def load_from_json_export(json_file):
    """Carga datos desde un archivo JSON exportado previamente."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        items = data.get('items', [])
        dependencies = data.get('dependencies', [])
        metadata = data.get('metadata', {})
        
        print(f"INFO: Cargado desde {json_file}")
        print(f"   📊 {len(items)} recursos, {len(dependencies)} dependencias")
        print(f"   📅 Exportado: {metadata.get('exported_at', 'desconocido')}")
        
        return items, dependencies
        
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR: No se pudo cargar {json_file}: {e}")
        return [], []

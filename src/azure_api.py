"""
Funciones para obtener y procesar datos de Azure (management groups, recursos, dependencias).
"""

import os
import sys
import json
import subprocess

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

def get_azure_management_groups():
    import platform
    if platform.system() == "Windows":
        return get_azure_management_groups_with_powershell()
    else:
        try:
            import requests
            token_cmd = ["az", "account", "get-access-token", "--resource", "https://management.azure.com/", "--output", "json"]
            token_result = subprocess.run(token_cmd, capture_output=True, text=True, check=True, encoding='utf-8')
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
            return mg_list
        except Exception as e:
            print(f"ADVERTENCIA: No se pudieron obtener management groups vía REST API: {e}")
            return []

def enrich_management_groups_with_ancestors(mg_list):
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
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
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

def run_az_graph_query_with_pagination(query):
    all_results = []
    skip_token = None
    while True:
        cmd = ["az", "graph", "query", "-q", query, "--first", "1000", "--output", "json"]
        if skip_token:
            cmd += ["--skip-token", skip_token]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        data = json.loads(result.stdout)
        all_results.extend(data.get('data', []))
        skip_token = data.get('skipToken')
        if not skip_token:
            break
    return all_results

def get_azure_resources():
    print("INFO: Obteniendo management groups (REST API o PowerShell) y recursos con az graph query...")
    if not os.system("az version > " + ("nul" if os.name == 'nt' else "/dev/null 2>&1")) == 0:
        print("\nERROR: Azure CLI no está instalado o no está en el PATH.")
        sys.exit(1)
    mg_items = get_azure_management_groups()
    mg_items = enrich_management_groups_with_ancestors(mg_items)
    try:
        rest_query = "resourcecontainers | where type != 'microsoft.management/managementgroups' | union resources"
        rest_items = run_az_graph_query_with_pagination(rest_query)
        print(f"INFO: Se han encontrado {len(rest_items)} recursos y resource containers (sin management groups).")
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
                        'vnetId': vnet_id
                    }
                    extra_subnets.append(subnet_item)
        if extra_subnets:
            print(f"INFO: Se han añadido {len(extra_subnets)} subnets como nodos independientes.")
        all_items = mg_items + rest_items + extra_subnets
        print(f"INFO: Total de elementos combinados: {len(all_items)}")
        return all_items
    except Exception as e:
        print(f"\nERROR al ejecutar 'az graph query': {e}")
        print("Asegúrate de haber iniciado sesión ('az login') y tener los permisos necesarios.")
        sys.exit(1)

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
        def scan_properties(props):
            if isinstance(props, dict):
                for k, value in props.items():
                    if isinstance(value, str) and '/subnets/' in value.lower():
                        subnet_id = value.lower()
                        if subnet_id in all_item_ids and subnet_id != source_id_lower:
                            dependencies.add((source_id_lower, subnet_id))
                            continue
                    if k.lower() == 'userassignedidentities' and isinstance(value, dict):
                        for mi_id in value.keys():
                            mi_id_lower = mi_id.lower()
                            if mi_id_lower in managed_identity_ids and mi_id_lower != source_id_lower:
                                dependencies.add((source_id_lower, mi_id_lower))
                    scan_properties(value)
            elif isinstance(props, list):
                for element in props: scan_properties(element)
            elif isinstance(props, str):
                if '/subnets/' in props.lower() and props.lower() in all_item_ids and props.lower() != source_id_lower:
                    dependencies.add((source_id_lower, props.lower()))
                elif props.lower() in all_item_ids and props.lower() != source_id_lower:
                    dependencies.add((source_id_lower, props.lower()))
        scan_properties(item)
    print(f"INFO: Se han encontrado {len(dependencies)} relaciones de dependencia.")
    return list(dependencies)

#!/usr/bin/env python3
"""
Layout de red simplificado con grid dinámico sin colisiones
"""

import math
from typing import List, Dict, Tuple, Any, Optional

def generate_network_layout(items: List[Dict], dependencies: List[Dict], include_ids: Optional[List[str]] = None) -> Tuple[List[Dict], Dict[int, Tuple[int, int]], Dict[int, str]]:
    """
    Genera layout de red con algoritmo grid dinámico simplificado que elimina colisiones.
    
    Returns:
        Tuple de (group_info, node_positions, resource_to_parent_id)
    """
    print("🔍 Analizando recursos para diagrama de red...")
    
    # Estructuras de datos principales
    group_info = []
    node_positions = {}
    resource_to_parent_id = {}
    
    # Contadores globales para IDs únicos
    global_sub_counter = 0
    global_rg_counter = 0
    
    # 1. ORGANIZACIÓN JERÁRQUICA DE DATOS
    # Clasificar recursos por Management Group → Subscription → Resource Group
    management_groups = {}
    subnet_resources = {}  # subnet_id → lista de recursos en esa subnet
    
    # Analizar todos los recursos y organizarlos jerárquicamente
    for i, item in enumerate(items):
        resource_type = (item.get('type') or '').lower()
        resource_id = item['id'].lower()
        
        if resource_type == 'microsoft.resources/subscriptions':
            # Es una subscription
            subscription_id = resource_id
            subscription_name = item.get('name', 'Subscription')
            
            # Determinar management group (simplificado)
            mg_name = 'Default Management Group'
            
            if mg_name not in management_groups:
                management_groups[mg_name] = {'subscriptions': {}}
            
            if subscription_id not in management_groups[mg_name]['subscriptions']:
                management_groups[mg_name]['subscriptions'][subscription_id] = {
                    'item': item,
                    'index': i,
                    'resource_groups': {}
                }
        
        elif resource_type == 'microsoft.resources/subscriptions/resourcegroups':
            # Es un resource group
            rg_id = resource_id
            parts = rg_id.split('/')
            subscription_id = '/'.join(parts[:3])  # /subscriptions/{sub-id}
            
            # Buscar la subscription en management groups
            for mg_name, mg_data in management_groups.items():
                if subscription_id in mg_data['subscriptions']:
                    mg_data['subscriptions'][subscription_id]['resource_groups'][rg_id] = {
                        'item': item,
                        'index': i,
                        'resources': []
                    }
                    break
        
        elif resource_type == 'microsoft.network/virtualnetworks/subnets':
            # Es una subnet - inicializar lista de recursos
            subnet_id = resource_id
            subnet_resources[subnet_id] = []
        
        else:
            # Es un recurso regular - asignar a su Resource Group
            parts = resource_id.split('/')
            if len(parts) >= 5:
                rg_id = '/'.join(parts[:5])  # /subscriptions/{sub}/resourceGroups/{rg}
                
                # Buscar el RG en la estructura
                for mg_name, mg_data in management_groups.items():
                    for sub_id, sub_data in mg_data['subscriptions'].items():
                        if rg_id in sub_data['resource_groups']:
                            sub_data['resource_groups'][rg_id]['resources'].append((i, item))
                            break
    
    # 2. DETECTAR ASOCIACIONES DE SUBNET PARA RECURSOS DE RED
    for i, item in enumerate(items):
        resource_type = (item.get('type') or '').lower()
        
        if resource_type not in ['microsoft.network/virtualnetworks', 'microsoft.network/virtualnetworks/subnets', 'microsoft.resources/subscriptions/resourcegroups', 'microsoft.resources/subscriptions']:
            # Buscar referencias a subnet en las propiedades
            props = item.get('properties') or {}
            subnet_refs = []
            
            # Para Network Interfaces, buscar en ipConfigurations
            if resource_type == 'microsoft.network/networkinterfaces':
                ip_configs = props.get('ipConfigurations', [])
                for ip_config in ip_configs:
                    subnet_id = (ip_config.get('properties', {}) or {}).get('subnet', {}).get('id')
                    if subnet_id:
                        subnet_refs.append(subnet_id.lower())
                        print(f"🔗 NIC {item.get('name')} detectada con subnet {subnet_id}")
                        break
            
            # Agregar recurso a la subnet correspondiente
            for subnet_ref in subnet_refs:
                if subnet_ref in subnet_resources:
                    subnet_resources[subnet_ref].append((i, item))
    
    # 3. LAYOUT PRINCIPAL - Grid dinámico sin colisiones
    print("📋 Posicionando Management Groups y Subscriptions...")
    
    current_y = 50
    
    for mg_name, mg_data in sorted(management_groups.items()):
        if mg_data['subscriptions']:
            print(f"🏢 Management Group: {mg_name} ({len(mg_data['subscriptions'])} subs)")
            
            # Para cada subscription
            for sub_id, sub_data in mg_data['subscriptions'].items():
                print(f"   📁 Subscription: {sub_data['item'].get('name', sub_id)}")
                
                # 💡 ALGORITMO GRID DINÁMICO SIMPLIFICADO
                rg_list = list(sub_data['resource_groups'].items())
                num_rgs = len(rg_list)
                
                if num_rgs == 0:
                    continue
                
                # Grid responsivo: más RGs = más columnas
                if num_rgs <= 2:
                    grid_cols = num_rgs
                elif num_rgs <= 6:
                    grid_cols = 3
                elif num_rgs <= 12:
                    grid_cols = 4
                else:
                    grid_cols = 5
                
                grid_rows = math.ceil(num_rgs / grid_cols)
                
                # Dimensiones fijas para consistencia
                rg_width = 650
                rg_height = 500
                grid_spacing_x = 100
                grid_spacing_y = 120
                
                sub_width = (grid_cols * rg_width) + ((grid_cols + 1) * grid_spacing_x) + 100
                sub_height = (grid_rows * rg_height) + ((grid_rows + 1) * grid_spacing_y) + 150
                
                print(f"   📐 Grid {grid_cols}x{grid_rows} para {num_rgs} RGs → Container: {sub_width}x{sub_height}")
                
                # Crear subscription container
                sub_group_id = f"group_subscription_{global_sub_counter}"
                global_sub_counter += 1
                
                group_info.append({
                    'id': sub_group_id,
                    'parent_id': '1',
                    'type': 'subscription_container',
                    'x': 50,
                    'y': current_y,
                    'width': sub_width,
                    'height': sub_height,
                    'label': f'🏢 {sub_data["item"].get("name", "Subscription")}',
                    'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#e3f2fd;strokeColor=#1976d2;fontSize=16;fontStyle=1;align=left;verticalAlign=top;spacingLeft=15;spacingTop=15;'
                })
                
                # Posicionar subscription item
                if sub_data['index'] is not None:
                    node_positions[sub_data['index']] = (20, 25)
                    resource_to_parent_id[sub_data['index']] = sub_group_id
                
                # Posicionar Resource Groups en grid perfecto
                print(f"      📦 Distribuyendo {num_rgs} Resource Groups en grid...")
                
                for idx, (rg_id, rg_data) in enumerate(rg_list):
                    # Calcular posición en grid
                    grid_row = idx // grid_cols
                    grid_col = idx % grid_cols
                    
                    # Posición absoluta sin colisiones
                    rg_x = grid_spacing_x + (grid_col * (rg_width + grid_spacing_x))
                    rg_y = 100 + grid_spacing_y + (grid_row * (rg_height + grid_spacing_y))
                    
                    rg_group_id = f"group_rg_{global_rg_counter}"
                    global_rg_counter += 1
                    
                    # Crear container del Resource Group
                    group_info.append({
                        'id': rg_group_id,
                        'parent_id': sub_group_id,
                        'type': 'resource_group_container',
                        'x': rg_x,
                        'y': rg_y,
                        'width': rg_width,
                        'height': rg_height,
                        'label': '',
                        'style': 'container=1;rounded=1;whiteSpace=wrap;html=1;fillColor=#fff8e1;strokeColor=#f9a825;fontSize=12;align=left;verticalAlign=top;'
                    })
                    
                    # Posicionar el ícono del Resource Group
                    if rg_data['index'] is not None:
                        node_positions[rg_data['index']] = (15, 15)
                        resource_to_parent_id[rg_data['index']] = rg_group_id
                    
                    # Posicionar recursos dentro del Resource Group
                    resources = rg_data['resources']
                    if resources:
                        print(f"🔧 RG {rg_data['item'].get('name', 'N/A')}: {len(resources)} recursos")
                        
                        # Grid simple para recursos
                        resources_per_row = 3
                        resource_width = 100
                        resource_height = 80
                        resource_spacing_x = 50
                        resource_spacing_y = 50
                        start_x = 60
                        start_y = 60
                        
                        for res_idx, (res_index, res_item) in enumerate(resources):
                            res_row = res_idx // resources_per_row
                            res_col = res_idx % resources_per_row
                            
                            res_x = start_x + (res_col * (resource_width + resource_spacing_x))
                            res_y = start_y + (res_row * (resource_height + resource_spacing_y))
                            
                            # Verificar límites del container
                            if res_x + resource_width > rg_width - 20:
                                res_row += 1
                                res_col = 0
                                res_x = start_x
                                res_y = start_y + (res_row * (resource_height + resource_spacing_y))
                            
                            node_positions[res_index] = (res_x, res_y)
                            resource_to_parent_id[res_index] = rg_group_id
                        
                        print(f"   ✅ Posicionados {len(resources)} recursos en RG")
                
                # Avanzar Y para próxima subscription
                current_y += sub_height + 200
    
    # 4. VERIFICACIÓN FINAL DE COLISIONES
    print("🔍 Verificando colisiones finales...")
    collision_detector = CollisionDetector()
    
    for index, (x, y) in node_positions.items():
        collision_detector.add_object(f"resource_{index}", x, y, 100, 80)
    
    final_collisions = collision_detector.detect_all_collisions()
    if final_collisions:
        print(f"⚠️  {len(final_collisions)} colisiones detectadas")
        for obj1, obj2 in final_collisions[:5]:
            print(f"⚠️  Colisión entre recursos: {obj1} ↔ {obj2}")
        if len(final_collisions) > 5:
            print(f"⚠️  ... y {len(final_collisions) - 5} colisiones más")
    else:
        print("✅ ¡Ninguna colisión detectada! Grid dinámico funcionando correctamente.")
    
    print(f"✅ Layout de red completado: {len(node_positions)} recursos posicionados")
    
    return group_info, node_positions, resource_to_parent_id


class CollisionDetector:
    """Detector de colisiones simplificado"""
    
    def __init__(self):
        self.objects = {}
    
    def add_object(self, obj_id, x, y, width, height):
        self.objects[obj_id] = {'x': x, 'y': y, 'width': width, 'height': height}
    
    def detect_all_collisions(self):
        collisions = []
        objects_list = list(self.objects.items())
        
        for i, (id1, obj1) in enumerate(objects_list):
            for id2, obj2 in objects_list[i+1:]:
                if self._objects_overlap(obj1, obj2):
                    collisions.append((id1, id2))
        
        return collisions
    
    def _objects_overlap(self, obj1, obj2):
        return not (obj1['x'] + obj1['width'] <= obj2['x'] or 
                   obj2['x'] + obj2['width'] <= obj1['x'] or
                   obj1['y'] + obj1['height'] <= obj2['y'] or
                   obj2['y'] + obj2['height'] <= obj1['y'])

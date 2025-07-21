"""
Layout para diagrama de componentes - agrupado por función/tipo
"""

from .utils import classify_network_resource, group_resources_by_type


def generate_components_layout(items, dependencies, levels, mg_id_to_idx, sub_id_to_idx, rg_id_to_idx):
    """Disposición para diagrama de componentes - agrupado por función/tipo"""
    print("🧩 Generando layout de componentes agrupado por función...")
    
    y_step = 180
    x_step = 200
    node_positions = {}
    
    # Agrupar recursos por tipo/función
    groups = {
        'Governance': [],  # Management groups, suscripciones
        'Compute': [],     # VMs, App Services, AKS
        'Storage': [],     # Storage accounts, disks
        'Network': [],     # VNets, load balancers, firewalls
        'Database': [],    # SQL, CosmosDB
        'Security': [],    # Key Vault, managed identity
        'AI/ML': [],       # Cognitive services, ML workspaces
        'Management': [],  # Log Analytics, Application Insights
        'Other': []        # Resto
    }
    
    # Clasificar recursos por grupo funcional
    for i, item in enumerate(items):
        resource_type = (item.get('type') or '').lower()
        
        # Governance - Management Groups, Suscripciones, Resource Groups
        if resource_type in [
            'microsoft.management/managementgroups', 
            'microsoft.resources/subscriptions', 
            'microsoft.resources/subscriptions/resourcegroups'
        ]:
            groups['Governance'].append((i, item))
        
        # Compute - VMs, App Services, Container Services
        elif any(compute_type in resource_type for compute_type in [
            'compute/virtualmachines', 'web/sites', 'containerservice', 
            'web/serverfarms', 'compute/availabilitysets', 'compute/virtualmachinescalesets'
        ]):
            groups['Compute'].append((i, item))
        
        # Storage - Storage Accounts, Disks
        elif any(storage_type in resource_type for storage_type in [
            'storage/storageaccounts', 'compute/disks', 'compute/diskencryptionsets'
        ]):
            groups['Storage'].append((i, item))
        
        # Network - Redes, Load Balancers, Firewalls
        elif 'network/' in resource_type:
            groups['Network'].append((i, item))
        
        # Database - SQL, CosmosDB, etc.
        elif any(db_type in resource_type for db_type in [
            'sql/', 'documentdb/', 'dbfor', 'cache/', 'search/'
        ]):
            groups['Database'].append((i, item))
        
        # Security - Key Vault, Managed Identity, Security
        elif any(sec_type in resource_type for sec_type in [
            'keyvault/', 'security/', 'managedidentity/', 'aad/'
        ]):
            groups['Security'].append((i, item))
        
        # AI/ML - Cognitive Services, Machine Learning
        elif any(ai_type in resource_type for ai_type in [
            'cognitiveservices/', 'machinelearningservices/', 'databricks/'
        ]):
            groups['AI/ML'].append((i, item))
        
        # Management - Monitoring, Analytics, Automation
        elif any(mgmt_type in resource_type for mgmt_type in [
            'insights/', 'operationalinsights/', 'automation/', 
            'operationsmanagement/', 'recoveryservices/'
        ]):
            groups['Management'].append((i, item))
        
        # Messaging & Integration
        elif any(msg_type in resource_type for msg_type in [
            'servicebus/', 'eventgrid/', 'logic/', 'apimanagement/'
        ]):
            # Agregar al grupo Management por ahora, o crear un grupo separado
            groups['Management'].append((i, item))
        
        # CDN & Media
        elif any(cdn_type in resource_type for cdn_type in [
            'cdn/', 'media/'
        ]):
            groups['Network'].append((i, item))  # Relacionado con distribución de contenido
        
        else:
            groups['Other'].append((i, item))
    
    print("📊 Distribución por grupos:")
    for group_name, group_items in groups.items():
        if group_items:
            print(f"   {group_name}: {len(group_items)} recursos")
    
    # Posicionar grupos verticalmente
    group_y = 100  # Espacio para títulos
    total_positioned = 0
    
    for group_name, group_items in groups.items():
        if not group_items:
            continue
        
        print(f"📍 Posicionando grupo {group_name} con {len(group_items)} recursos")
        
        # Posicionar recursos del grupo horizontalmente
        x = 100
        resources_per_row = 5  # Máximo 5 recursos por fila
        current_row = 0
        
        for i, (idx, item) in enumerate(group_items):
            # Calcular posición en grid
            col = i % resources_per_row
            row = i // resources_per_row
            
            pos_x = x + col * x_step
            pos_y = group_y + row * 100  # Espaciado vertical dentro del grupo
            
            node_positions[idx] = (pos_x, pos_y)
            total_positioned += 1
        
        # Calcular espacio necesario para este grupo
        rows_needed = (len(group_items) + resources_per_row - 1) // resources_per_row
        group_height = max(100, rows_needed * 100)  # Altura mínima de 100px
        
        group_y += group_height + y_step  # Espacio entre grupos
    
    print(f"✅ Layout de componentes completado: {total_positioned} recursos posicionados")
    return node_positions


def classify_resource_by_function(resource_type):
    """
    Clasifica un recurso por su función principal.
    
    Args:
        resource_type (str): Tipo de recurso de Azure
        
    Returns:
        str: Categoría funcional
    """
    resource_type_lower = resource_type.lower()
    
    # Governance
    if any(gov_type in resource_type_lower for gov_type in [
        'management/managementgroups', 'resources/subscriptions'
    ]):
        return 'Governance'
    
    # Compute
    if any(compute_type in resource_type_lower for compute_type in [
        'compute/virtualmachines', 'web/', 'containerservice'
    ]):
        return 'Compute'
    
    # Storage
    if any(storage_type in resource_type_lower for storage_type in [
        'storage/', 'compute/disks'
    ]):
        return 'Storage'
    
    # Network
    if 'network/' in resource_type_lower:
        return 'Network'
    
    # Database
    if any(db_type in resource_type_lower for db_type in [
        'sql/', 'documentdb/', 'cache/', 'search/'
    ]):
        return 'Database'
    
    # Security
    if any(sec_type in resource_type_lower for sec_type in [
        'keyvault/', 'security/', 'managedidentity/'
    ]):
        return 'Security'
    
    # AI/ML
    if any(ai_type in resource_type_lower for ai_type in [
        'cognitiveservices/', 'machinelearningservices/', 'databricks/'
    ]):
        return 'AI/ML'
    
    # Management
    if any(mgmt_type in resource_type_lower for mgmt_type in [
        'insights/', 'operationalinsights/', 'automation/'
    ]):
        return 'Management'
    
    return 'Other'

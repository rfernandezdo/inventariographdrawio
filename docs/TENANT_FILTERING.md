# Filtrado por Tenant - Azure Infrastructure Diagram Generator

## Descripción

El sistema ahora incluye capacidades de filtrado por **Tenant ID** para generar diagramas específicos de un tenant de Azure. Esta funcionalidad es especialmente útil cuando se tiene acceso a múltiples tenants y se desea crear diagramas separados para cada uno.

## Problema Solucionado

Antes de esta implementación, el sistema mezclaba recursos de diferentes tenants en un solo diagrama, lo cual creaba confusión y hacía difícil la gestión de infraestructuras multi-tenant. Por ejemplo:

- **Tenant A (Corporativo)**: `aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee`
- **Tenant B (Desarrollo)**: `ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj`

Ambos tenants aparecían mezclados en el mismo diagrama, causando confusión organizacional.

## Funcionalidades Implementadas

### 1. Detección Automática del Tenant Actual

Por defecto, el sistema usa el tenant del contexto actual del CLI de Azure:

```bash
python src/cli.py  # Usa automáticamente el tenant actual
```

### 2. Filtrado por Tenant Específico

Permite especificar un tenant específico:

```bash
python src/cli.py --tenant-filter aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
```

### 3. Listado de Tenants Disponibles

Muestra todos los tenants accesibles desde el CLI de Azure:

```bash
python src/cli.py --list-tenants
```

### 5. Comportamiento por Defecto

```bash
# Por defecto, usa el tenant actual automáticamente
python src/cli.py

# Equivalente a:
python src/cli.py --tenant-filter $(az account show --query tenantId -o tsv)
```

**Salida de ejemplo:**
```
=== TENANTS DISPONIBLES ===
• Corporativo
  Tenant ID: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
  Subscription ID: 11111111-2222-3333-4444-555555555555 ← (ejemplo)

• Desarrollo
  Tenant ID: ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj
  Subscription ID: 66666666-7777-8888-9999-aaaaaaaaaaaa
```

## Implementación Técnica

### Nuevos Parámetros CLI

- `--tenant-filter TENANT_ID`: Filtrar por Tenant ID específico
- `--all-tenants`: Incluir recursos de todos los tenants (desactiva filtrado)
- `--list-tenants`: Listar todos los tenants disponibles

### Funciones Añadidas en `azure_api.py`

1. **`get_current_tenant_id()`**: Obtiene el tenant actual del CLI de Azure
2. **`list_available_tenants()`**: Lista todos los tenants accesibles
3. **`filter_items_by_tenant(items, tenant_id)`**: Filtra recursos por tenant

### Lógica de Filtrado

El filtrado se aplica en múltiples niveles:

1. **Management Groups**: Filtrados por `tenantId`
2. **Suscripciones**: Filtradas por `tenantId`
3. **Resource Groups**: Filtrados por `tenantId`
4. **Recursos**: Filtrados por `tenantId`
5. **Subnets**: Heredan el tenant de su VNet padre

### Sistema de Caché Mejorado

El caché ahora incluye el tenant en el nombre del archivo:

```
.azure_cache/final_inventory_aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee_20250805_13.json
.azure_cache/final_inventory_ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj_20250805_13.json
```

## Casos de Uso

### 1. Diagrama para Tenant Actual

```bash
# Genera diagrama solo para el tenant actual
python src/cli.py --diagram-mode infrastructure --output tenant_actual.drawio
```

### 2. Diagramas Separados por Tenant

```bash
# Tenant Corporativo
python src/cli.py --tenant-filter aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee \
  --diagram-mode infrastructure --output corporativo.drawio

# Tenant Desarrollo
python src/cli.py --tenant-filter ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj \
  --diagram-mode infrastructure --output desarrollo.drawio
```

### 3. Exploración de Tenants

```bash
# Listar tenants disponibles
python src/cli.py --list-tenants

# Generar diagramas de red para cada tenant
python src/cli.py --tenant-filter TENANT_ID --diagram-mode network
```

### 4. Filtrado con JSON Exportado

```bash
# Exportar datos con tenant específico
python src/cli.py --tenant-filter TENANT_ID --export-json tenant_data.json

# Usar datos exportados (el filtrado ya está aplicado)
python src/cli.py --input-json tenant_data.json --diagram-mode all
```

## Beneficios

1. **Claridad Organizacional**: Diagramas limpios por tenant
2. **Gestión Multi-Tenant**: Facilita la administración de múltiples tenants
3. **Cache Optimizado**: Cache separado por tenant para mejor rendimiento
4. **Compatibilidad**: Funciona con todos los modos de diagrama existentes
5. **Flexibilidad**: Detección automática o selección manual del tenant

## Validación de Resultados

El sistema proporciona información clara sobre el filtrado:

```
INFO: Filtrando recursos por tenant: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
INFO: Filtrado por tenant completado: 69 → 68 elementos

¡ÉXITO! Se ha creado el diagrama de 'infrastructure' en 'corporativo_only.drawio'.

Tenant filtrado: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
```

## Manejo de Errores

- **Tenant no encontrado**: El sistema filtra sin errores, resultando en diagramas vacíos si el tenant no tiene recursos
- **Sin permisos**: Los errores de Azure CLI se manejan apropiadamente
- **Recursos sin tenant**: Se incluyen con advertencia para evitar pérdida de datos

## Compatibilidad

Esta funcionalidad es completamente compatible con:

- ✅ Todos los modos de diagrama (`infrastructure`, `components`, `network`, `all`)
- ✅ Sistema de caché existente
- ✅ Opciones de filtrado por IDs (`--include-ids`, `--exclude-ids`)
- ✅ Exportación e importación de JSON
- ✅ Opciones de embebido de datos

## Limitaciones

- Requiere que el CLI de Azure esté autenticado con los tenants objetivo
- El filtrado se basa en el campo `tenantId` de los recursos de Azure
- Resources sin `tenantId` se incluyen con advertencia para prevenir pérdida de datos

---

**Ejemplo de flujo de trabajo multi-tenant:**

```bash
# 1. Listar tenants disponibles
python src/cli.py --list-tenants

# 2. Generar diagrama para cada tenant
python src/cli.py --tenant-filter aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee -o corporativo.drawio
python src/cli.py --tenant-filter ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj -o desarrollo.drawio

# 3. Resultado: Diagramas completamente separados por tenant
```

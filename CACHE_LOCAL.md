# Cache Local y Procesamiento Posterior

El sistema ahora incluye funcionalidad de **cache local** que permite:

1. **Almacenar consultas Azure localmente** para evitar repetir llamadas costosas
2. **Exportar datos a JSON** para procesamiento posterior sin conexión a Azure
3. **Generar múltiples diagramas** desde el mismo conjunto de datos

## 🚀 Casos de Uso

### Desarrollo y Testing
```bash
# Primera ejecución: consulta Azure y crea cache
python3 src/cli.py --diagram-mode infrastructure

# Ejecuciones posteriores: usa cache (mucho más rápido)
python3 src/cli.py --diagram-mode network
python3 src/cli.py --diagram-mode components
```

### Presentaciones y Demos
```bash
# Capturar snapshot de la infraestructura
python3 src/cli.py --export-json infraestructura_$(date +%Y%m%d).json

# Generar diagramas offline para presentación
python3 src/cli.py --input-json infraestructura_20241226.json --diagram-mode network
```

### CI/CD y Automatización
```bash
# En el pipeline: capturar datos una vez
python3 src/cli.py --export-json pipeline_data.json

# Generar múltiples outputs
python3 src/cli.py --input-json pipeline_data.json --diagram-mode infrastructure --output infra.drawio
python3 src/cli.py --input-json pipeline_data.json --diagram-mode network --output network.drawio
python3 src/cli.py --input-json pipeline_data.json --diagram-mode components --output components.drawio
```

## 📖 Opciones de Línea de Comandos

### Cache
- `--no-cache`: No usar cache, siempre consultar Azure
- `--force-refresh`: Forzar actualización eliminando cache existente
- `--clear-cache`: Limpiar todo el cache local

### Exportación/Importación
- `--export-json ARCHIVO`: Exportar datos consultados a JSON
- `--input-json ARCHIVO`: Usar datos desde JSON (sin consultar Azure)
- `--output ARCHIVO`: Especificar archivo de salida del diagrama

## 🗂️ Estructura del Cache

```
.azure_cache/
├── management_groups_2024122614.json    # Management groups
├── graph_query_all_resources_2024122614.json    # Recursos principales
└── final_inventory_2024122614.json      # Inventario completo combinado
```

Los archivos de cache incluyen timestamp en el nombre y **expiran automáticamente** después de 4 horas.

## 📋 Ejemplos Prácticos

### 1. Workflow Básico
```bash
# Consulta inicial (lenta, crea cache)
python3 src/cli.py --diagram-mode infrastructure
# ⏱️ ~30-60 segundos

# Consultas posteriores (rápidas, usa cache)
python3 src/cli.py --diagram-mode network
# ⏱️ ~2-5 segundos
```

### 2. Exportar para Uso Posterior
```bash
# Exportar datos actuales
python3 src/cli.py --export-json mi_infraestructura.json

# Usar datos exportados días/semanas después
python3 src/cli.py --input-json mi_infraestructura.json --diagram-mode network
```

### 3. Análisis Offline
```bash
# En la oficina: capturar datos
python3 src/cli.py --export-json datos_cliente.json

# En casa/viaje: trabajar offline
python3 src/cli.py --input-json datos_cliente.json --diagram-mode components
```

### 4. Forzar Actualización
```bash
# Si la infraestructura cambió significativamente
python3 src/cli.py --force-refresh --diagram-mode infrastructure
```

### 5. Gestión del Cache
```bash
# Ver cache actual
ls -la .azure_cache/

# Limpiar cache
python3 src/cli.py --clear-cache

# Ver tamaño del cache
du -sh .azure_cache/
```

## 🔧 Configuración Avanzada

### Cambiar Duración del Cache
Edita `src/azure_api.py`:
```python
CACHE_EXPIRY_HOURS = 8  # Cache válido por 8 horas
```

### Ubicación del Cache
Por defecto: `.azure_cache/` en el directorio actual.
Para cambiar, edita:
```python
CACHE_DIR = Path('/tmp/azure_cache')  # Cache en /tmp
```

## 📊 Formato del JSON Exportado

```json
{
  "metadata": {
    "exported_at": "2024-12-26T14:30:00",
    "total_items": 156,
    "total_dependencies": 89
  },
  "items": [
    {
      "id": "/subscriptions/...",
      "name": "Mi Suscripción",
      "type": "Microsoft.Resources/subscriptions",
      "properties": { ... }
    }
  ],
  "dependencies": [
    ["/subscriptions/abc", "/subscriptions/abc/resourceGroups/rg1"]
  ]
}
```

## ⚡ Ventajas del Cache

| Aspecto | Sin Cache | Con Cache |
|---------|-----------|-----------|
| **Primera ejecución** | 30-60 seg | 30-60 seg |
| **Ejecuciones posteriores** | 30-60 seg | 2-5 seg |
| **Dependencia de red** | Siempre | Solo primera vez |
| **Consistencia datos** | Variable | Garantizada |
| **Desarrollo iterativo** | Lento | Rápido |

## 🛠️ Troubleshooting

### Cache Corrupto
```bash
python3 src/cli.py --clear-cache
python3 src/cli.py --force-refresh
```

### Datos Obsoletos
```bash
# Verificar edad del cache
ls -la .azure_cache/

# Forzar actualización si es necesario
python3 src/cli.py --force-refresh
```

### JSON No Carga
- Verificar que el archivo existe y es válido JSON
- Regenerar desde cache: `python3 -c "from src.azure_api import export_cache_to_json; export_cache_to_json('nuevo.json')"`

### Sin Permisos de Escritura
```bash
# Verificar permisos del directorio
ls -la .
mkdir -p .azure_cache
chmod 755 .azure_cache
```

## 📈 Comparación de Rendimiento

```bash
# Medir tiempo sin cache
time python3 src/cli.py --no-cache --diagram-mode network

# Medir tiempo con cache
time python3 src/cli.py --diagram-mode network

# Medir desde JSON
time python3 src/cli.py --input-json datos.json --diagram-mode network
```

Resultados típicos:
- **Sin cache**: ~45 segundos
- **Con cache**: ~3 segundos  
- **Desde JSON**: ~1 segundo

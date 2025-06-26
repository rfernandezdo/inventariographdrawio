# Microsoft Azure dynamic diagrams with draw.io and Azure Resource Graph

Este proyecto permite generar diagramas automáticos de topologías y recursos de Azure en draw.io, a partir de datos reales obtenidos mediante Azure Resource Graph.

## Objetivo
- Automatizar la creación de diagramas de arquitectura Azure en draw.io, exportando los recursos a CSV y usando la función de importación de draw.io.
- Facilitar la visualización y documentación de entornos Azure de forma dinámica y actualizable.

## Estructura del Proyecto

```
├── src/                    # Código fuente principal
│   ├── cli.py             # Interfaz de línea de comandos
│   ├── azure_api.py       # Interacción con Azure Resource Graph
│   ├── drawio_export.py   # Generación de archivos .drawio
│   └── utils.py           # Utilidades comunes
├── tests/                 # Tests y pruebas
│   ├── fixtures/          # Archivos de prueba (.drawio)
│   └── test_*.py          # Scripts de test
├── examples/              # Scripts de ejemplo y demos
├── docs/                  # Documentación
├── data/                  # Archivos de datos y ejemplos
└── README.md              # Este archivo
```

## Requisitos
- Python 3.x
- Azure CLI (`az`) y extensión `az graph`
- Permisos de lectura en la suscripción de Azure

## Instalación
```bash
# Instalar dependencias si es necesario
pip install requests

# Asegurarse de tener Azure CLI y la extensión graph
az extension add --name resource-graph
```

## Uso Básico
```bash
# Generar diagrama con todos los recursos
python src/cli.py

# Generar en modo específico
python src/cli.py --diagram-mode network

# Exportar datos a JSON
python src/cli.py --export-json inventario.json

# Usar datos offline
python src/cli.py --input-json inventario.json --output diagrama_offline.drawio
```

## Modos de Diagrama
- `infrastructure`: Jerarquía completa (management groups, suscripciones, resource groups, recursos)
- `components`: Vista de componentes y sus relaciones
- `network`: Vista enfocada en recursos de red y conectividad

## Opciones Avanzadas
- `--no-embed-data`: No incrusta todos los datos en los nodos
- `--include-ids <id1> <id2>`: Solo incluye elementos específicos y sus descendientes
- `--exclude-ids <id1> <id2>`: Excluye elementos específicos
- `--clear-cache`: Limpia la cache local
- `--use-cache`: Fuerza el uso de cache (no consulta Azure)
## Visualización en draw.io
1. Abre el archivo generado en [draw.io](https://app.diagrams.net/)
2. Selecciona todo (Ctrl+A) y usa el menú `Organizar > Disposición > Gráfico Jerárquico` para organizar el diagrama.
3. Selecciona cualquier icono y presiona Ctrl+M (Cmd+M en Mac) para ver todos sus datos incrustados.

## Navegación por el diagrama
Seguir las instrucciones de [Step through your diagram using the explore function](https://www.drawio.com/doc/faq/explore-plugin)

## Tests y Ejemplos
```bash
# Ejecutar tests
python tests/test_simple.py
python tests/test_cache_system.py

# Ejecutar ejemplos
python examples/demo_cache_workflow.py
```

## Documentación
Ver el directorio `docs/` para documentación detallada sobre:
- Sistema de cache local
- Modos de diagrama
- Manejo de datos
- Mejoras planificadas

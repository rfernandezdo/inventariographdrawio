# Microsoft Azure dynamic diagrams with draw.io and Azure Resource Graph

Este proyecto permite generar diagramas automáticos de topologías y recursos de Azure en draw.io, a partir de datos reales obtenidos mediante Azure Resource Graph.

## Objetivo
- Automatizar la creación de diagramas de arquitectura Azure en draw.io, exportando los recursos a CSV y usando la función de importación de draw.io.
- Facilitar la visualización y documentación de entornos Azure de forma dinámica y actualizable.


# =============================
# Script Python: azure_to_drawio.py
# =============================

## Descripción
Este script genera un archivo `.drawio` con la jerarquía completa de recursos de Azure (management groups, suscripciones, resource groups, recursos, VNets, subnets, etc.) usando Azure Resource Graph y lo deja listo para abrir en [draw.io](https://app.diagrams.net/).

## Requisitos
- Python 3.x
- Azure CLI (`az`) y extensión `az graph`
- Permisos de lectura en la suscripción de Azure
- `pip install requests`

## Ejecución básica
```sh
python azure_to_drawio.py
```
Esto generará el archivo `azure_full_hierarchy_with_icons.drawio` con toda la jerarquía de tu tenant.

## Opciones avanzadas
Puedes filtrar el diagrama generado usando los siguientes parámetros:

- `--no-embed-data`: No incrusta todos los datos en los nodos, solo el campo `type` (reduce el tamaño del archivo).
- `--include-ids <id1> <id2> ...`: Solo incluye en el diagrama los elementos (management group, suscripción, resource group) cuyos IDs se indiquen y todos sus descendientes.
  - Ejemplo: `--include-ids /providers/Microsoft.Management/managementGroups/miMG /subscriptions/xxxx-xxxx-xxxx`
- `--exclude-ids <id1> <id2> ...`: Excluye del diagrama los elementos (y sus descendientes) cuyos IDs se indiquen.
  - Ejemplo: `--exclude-ids /subscriptions/xxxx-xxxx-xxxx`
- `-h`, `--help`: Muestra la ayuda extendida y termina.

Puedes combinar `--include-ids` y `--exclude-ids` para mayor control.

## Notas sobre los IDs
- Los IDs deben ser los IDs completos de Azure (puedes obtenerlos con `az account management-group list`, `az account list`, etc.).
- El archivo generado se llama por defecto `azure_full_hierarchy_with_icons.drawio`.

## Visualización en draw.io
1. Abre el archivo generado en [draw.io](https://app.diagrams.net/)
2. Selecciona todo (Ctrl+A) y usa el menú `Organizar > Disposición > Gráfico Jerárquico` para organizar el diagrama.
3. Selecciona cualquier icono y presiona Ctrl+M (Cmd+M en Mac) para ver todos sus datos incrustados.

## Navegar por el diagrama

Seguir las instrucciones de [Step through your diagram using the explore function](https://www.drawio.com/doc/faq/explore-plugin)

# Microsoft Azure dynamic diagrams with draw.io and Azure Resource Graph

Este proyecto permite generar diagramas automáticos de topologías y recursos de Azure en draw.io, a partir de datos reales obtenidos mediante Azure Resource Graph.

## Objetivo
- Automatizar la creación de diagramas de arquitectura Azure en draw.io, exportando los recursos a CSV y usando la función de importación de draw.io.
- Facilitar la visualización y documentación de entornos Azure de forma dinámica y actualizable.

## Flujo de trabajo
1. Ejecuta el script para generar el CSV de recursos Azure.
2. Importa el CSV en draw.io siguiendo la guía oficial: [Automáticamente crear diagramas draw.io desde CSV](https://about.draw.io/automatically-create-draw-io-diagrams-from-csv-files/).
3. Personaliza y comparte el diagrama generado.

## Características principales
- Modularización por tipo de recurso (VNet, Subnet, NIC, VM, Disk, AvailabilitySet)
- Parámetros configurables y soporte de configuración externa (JSON)
- Validaciones de entorno y mensajes de error claros
- Exportación a CSV (compatible draw.io) y JSON
- Limpieza automática de referencias para draw.io
- Pruebas automáticas con Pester
- Integración continua con GitHub Actions

## Requisitos
- Azure CLI (`az`) y extensión `az graph`
- PowerShell Core (`pwsh`)
- Permisos de lectura en la suscripción de Azure

## Instalación rápida
1. Clona el repositorio
2. Instala Azure CLI y la extensión:
   ```sh
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   az extension add --name resource-graph
   az login
   ```
3. Instala PowerShell Core si no lo tienes: [Guía oficial](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-linux?view=powershell-7.5)

## Ejecución básica
```sh
pwsh ./src/InventarioAzure.ps1
```

## Ejecución avanzada
Con parámetros:
```sh
pwsh ./src/InventarioAzure.ps1 -ResourceType VNet,VM -OutputFile inventario.csv -OutputFormat CSV
```
Con archivo de configuración:
```sh
pwsh ./src/InventarioAzure.ps1 -ConfigFile ./config/config-avanzado.json
```

## Importar el CSV en draw.io
1. Abre [draw.io](https://app.diagrams.net/)
2. Ve a `Archivo > Importar desde > CSV...`
3. Selecciona el archivo generado (`inventario.csv` o similar)
4. Sigue la guía oficial: [Automáticamente crear diagramas draw.io desde CSV](https://about.draw.io/automatically-create-draw-io-diagrams-from-csv-files/)

## Ejemplo de configuración avanzada (`config/config-avanzado.json`)
```json
{
  "OutputFile": "inventario-avanzado.json",
  "ResourceTypes": ["VNet", "Subnet", "NIC", "VM", "Disk", "AvailabilitySet"],
  "OutputFormat": "JSON",
  "SubscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "ResourceGroup": "mi-grupo-recursos",
  "TagFilter": {
    "Environment": "Production"
  },
  "ExtraFields": ["properties.provisioningState", "properties.addressSpace.addressPrefixes"]
}
```

## Ejemplo de código para lanzar el flujo completo y generar el CSV compatible draw.io
# 1. Ejecuta el script para tu suscripción activa:
pwsh ./src/InventarioAzure.ps1 -OutputFile drawio-azure-import.csv -OutputFormat CSV

# 2. (Opcional) Repite para otras suscripciones cambiando el contexto:
# az account set --subscription <id-o-nombre>
# pwsh ./src/InventarioAzure.ps1 -OutputFile drawio-azure-import-<otra>.csv -OutputFormat CSV

# 3. Importa el CSV en draw.io como se indica en el README

## Pruebas automáticas
```sh
pwsh -c 'Invoke-Pester -Path ./tests -Output Detailed'
```

## Integración continua
El repositorio incluye un workflow de GitHub Actions que ejecuta los tests automáticamente en cada push o pull request.

## Licencia
MIT

# =============================
# Script Python: azure_to_drawio.py
# =============================

## Descripción
Este script genera un archivo `.drawio` con la jerarquía completa de recursos de Azure (management groups, suscripciones, resource groups, recursos, VNets, subnets, etc.) usando Azure Resource Graph y lo deja listo para abrir en [draw.io](https://app.diagrams.net/).

## Requisitos
- Python 3.x
- Azure CLI (`az`) y extensión `az graph`
- Permisos de lectura en la suscripción de Azure

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

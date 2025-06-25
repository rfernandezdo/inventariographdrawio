"""
Funciones auxiliares y utilidades generales.
"""

def print_help_section():
    print("""
Opciones del script:
-------------------

Por defecto, el script genera el diagrama completo de la jerarquía de Azure.

Opciones disponibles:

  --no-embed-data
      No incrusta todos los datos en los nodos, solo el campo 'type'.
      Útil para reducir el tamaño del archivo .drawio.

  --include-ids <id1> <id2> ...
      Solo incluye en el diagrama los elementos (management group, suscripción, resource group) cuyos IDs se indiquen y todos sus descendientes.
      Ejemplo: --include-ids /providers/Microsoft.Management/managementGroups/miMG /subscriptions/xxxx-xxxx-xxxx

  --exclude-ids <id1> <id2> ...
      Excluye del diagrama los elementos (y sus descendientes) cuyos IDs se indiquen.
      Ejemplo: --exclude-ids /subscriptions/xxxx-xxxx-xxxx

  -h, --help
      Muestra esta ayuda y termina.

Notas:
- Los IDs deben ser los IDs completos de Azure (puedes obtenerlos con 'az account management-group list', 'az account list', etc.).
- Puedes combinar --include-ids y --exclude-ids para mayor control.
- El archivo generado se llama por defecto 'azure_full_hierarchy_with_icons.drawio'.

""")

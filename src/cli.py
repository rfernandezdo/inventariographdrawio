"""
Punto de entrada principal y lógica de línea de comandos.
"""

import argparse
import sys
from azure_api import get_azure_resources, find_dependencies
from drawio_export import generate_drawio_file, filter_items_and_dependencies
from utils import print_help_section

OUTPUT_FILENAME = "azure_full_hierarchy_with_icons.drawio"

def main():
    parser = argparse.ArgumentParser(description="Generador de Diagramas de Jerarquía de Azure para Draw.io", add_help=False)
    parser.add_argument('--no-embed-data', action='store_true', help='No incrustar todos los datos, solo el campo type')
    parser.add_argument('--include-ids', nargs='+', help='IDs de management group, suscripción o resource group a incluir (y sus descendientes)')
    parser.add_argument('--exclude-ids', nargs='+', help='IDs de management group, suscripción o resource group a excluir (y sus descendientes)')
    parser.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda y termina')
    args = parser.parse_args()

    if args.help:
        print_help_section()
        sys.exit(0)

    print("--- Generador de Diagramas de Jerarquía de Azure para Draw.io ---")
    azure_items = get_azure_resources()
    if not azure_items:
        print("\nAVISO: No se encontraron elementos. Revisa tu login ('az login') y permisos.")
        sys.exit(0)
    dependencies = find_dependencies(azure_items)
    # Filtrar si corresponde
    azure_items, dependencies = filter_items_and_dependencies(
        azure_items, dependencies, include_ids=args.include_ids, exclude_ids=args.exclude_ids)
    drawio_content = generate_drawio_file(azure_items, dependencies, embed_data=not args.no_embed_data, include_ids=args.include_ids)
    try:
        with open(OUTPUT_FILENAME, "w", encoding='utf-8') as f:
            f.write(drawio_content)
        print(f"\n¡ÉXITO! Se ha creado el archivo '{OUTPUT_FILENAME}'.")
        print("\n--- PRÓXIMOS PASOS ---")
        print("1. Abre el archivo en https://app.diagrams.net.")
        print("2. Organiza el diagrama: Selecciona todo (Ctrl+A) -> Menú 'Organizar' -> 'Disposición' -> 'Gráfico Jerárquico'.")
        print("\n3. Selecciona cualquier icono y presiona Ctrl+M (Cmd+M en Mac) para ver todos sus datos.")
    except IOError as e:
        print(f"\nERROR al escribir el archivo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

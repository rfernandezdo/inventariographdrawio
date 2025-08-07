"""
Punto de entrada principal y lógica de línea de comandos.
"""

import argparse
import os
import sys
from azure_api import get_azure_resources, find_dependencies, export_cache_to_json, load_from_json_export, clear_cache, get_current_tenant_id, list_available_tenants, check_azure_login
from drawio_export import generate_drawio_file, filter_items_and_dependencies
from utils import print_help_section

OUTPUT_FILENAME = "azure_full_hierarchy_with_icons.drawio"

def main():
    parser = argparse.ArgumentParser(description="Generador de Diagramas de Jerarquía de Azure para Draw.io", add_help=False)
    parser.add_argument('--diagram-mode', choices=['infrastructure', 'components', 'network', 'all'], default='infrastructure',
                       help='Tipo de diagrama a generar: infrastructure (jerarquía completa), components (agrupado por función), network (solo recursos de red), all (todos los modos en páginas separadas)')
    parser.add_argument('--no-embed-data', action='store_true', help='No incrustar todos los datos, solo el campo type')
    parser.add_argument('--no-hierarchy-edges', action='store_true', help='En modo network, ocultar enlaces jerárquicos (RGs y VNet-Subnet) manteniendo dependencias de red')
    parser.add_argument('--include-ids', nargs='+', help='IDs de management group, suscripción o resource group a incluir (y sus descendientes)')
    parser.add_argument('--exclude-ids', nargs='+', help='IDs de management group, suscripción o resource group a excluir (y sus descendientes)')
    
    # Opciones de filtrado por tenant
    parser.add_argument('--tenant-filter', metavar='TENANT_ID', help='Filtrar recursos por Tenant ID específico (por defecto: tenant actual del CLI de Azure)')
    parser.add_argument('--all-tenants', action='store_true', help='Incluir recursos de todos los tenants (desactiva el filtrado automático por tenant)')
    parser.add_argument('--list-tenants', action='store_true', help='Listar todos los tenants disponibles y salir')
    
    # Opciones de cache y almacenamiento local
    parser.add_argument('--no-cache', action='store_true', help='No usar cache local, siempre consultar Azure')
    parser.add_argument('--force-refresh', action='store_true', help='Forzar actualización eliminando cache existente')
    parser.add_argument('--export-json', metavar='FILE', help='Exportar datos a JSON para procesamiento posterior')
    parser.add_argument('--input-json', metavar='FILE', help='Usar datos desde archivo JSON previamente exportado')
    parser.add_argument('--clear-cache', action='store_true', help='Limpiar todo el cache local y salir')
    parser.add_argument('--output', '-o', metavar='FILE', help=f'Archivo de salida (por defecto: {OUTPUT_FILENAME})')
    
    parser.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda y termina')
    
    try:
        args = parser.parse_args()
    except SystemExit as e:
        print(f"ERROR: Error al parsear argumentos de línea de comandos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Error inesperado al parsear argumentos: {e}")
        sys.exit(1)

    if args.help:
        print_help_section()
        print("\n=== OPCIONES DE DIAGRAMA ===")
        print("--diagram-mode MODE  Tipo: infrastructure, components, network, all")
        print("--no-embed-data      No incrustar datos completos")
        print("--no-hierarchy-edges Quita enlaces jerárquicos (RGs y VNet-Subnet) manteniendo dependencias de red")
        print("--include-ids IDS    Incluir solo ciertos recursos")
        print("--exclude-ids IDS    Excluir ciertos recursos")
        print("\n=== OPCIONES DE FILTRADO POR TENANT ===")
        print("--tenant-filter ID   Filtrar por Tenant ID específico (por defecto: tenant actual)")
        print("--all-tenants        Incluir recursos de todos los tenants")
        print("--list-tenants       Listar todos los tenants disponibles")
        print("\n=== OPCIONES DE CACHE Y ALMACENAMIENTO LOCAL ===")
        print("--no-cache           No usar cache, siempre consultar Azure")
        print("--force-refresh      Forzar actualización eliminando cache")
        print("--export-json FILE   Exportar datos a JSON para uso posterior")
        print("--input-json FILE    Usar datos desde JSON (sin consultar Azure)")
        print("--clear-cache        Limpiar cache local")
        print("--output FILE        Archivo de salida")
        print("\nEjemplos:")
        print("  # Incluir todos los tenants:")
        print("  python src/cli.py --all-tenants")
        print("")
        print("  # Filtrar por tenant específico:")
        print("  python src/cli.py --tenant-filter aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        print("")
        print("  # Listar tenants disponibles:")
        print("  python src/cli.py --list-tenants")
        print("")
        print("  # Generar diagrama y exportar datos:")
        print("  python src/cli.py --export-json mi_inventario.json")
        print("")
        print("  # Usar datos exportados sin consultar Azure:")
        print("  python src/cli.py --input-json mi_inventario.json --diagram-mode network")
        print("")
        print("  # Forzar actualización del cache:")
        print("  python src/cli.py --force-refresh")
        sys.exit(0)

    # Listar tenants si se solicita
    if args.list_tenants:
        tenants = list_available_tenants()
        if tenants:
            current_tenant = get_current_tenant_id()
            print("\n=== TENANTS DISPONIBLES ===")
            for tenant in tenants:
                marker = " ← (actual)" if tenant['tenantId'] == current_tenant else ""
                print(f"• {tenant['name']}")
                print(f"  Tenant ID: {tenant['tenantId']}")
                print(f"  Subscription ID: {tenant['subscriptionId']}{marker}")
                print()
        else:
            print("No se pudieron obtener los tenants disponibles.")
        sys.exit(0)

    # Limpiar cache si se solicita
    if args.clear_cache:
        clear_cache()
        print("Cache eliminado exitosamente.")
        sys.exit(0)

    # Determinar archivo de salida
    output_file = args.output or OUTPUT_FILENAME

    # Determinar tenant para filtrar
    target_tenant = None
    if args.all_tenants:
        target_tenant = None
        print("INFO: Incluyendo recursos de todos los tenants")
    elif args.tenant_filter:
        target_tenant = args.tenant_filter
        print(f"INFO: Filtrando por tenant específico: {target_tenant}")
    else:
        target_tenant = get_current_tenant_id()
        if target_tenant:
            print(f"INFO: Usando tenant actual por defecto: {target_tenant}")
        else:
            print("ADVERTENCIA: No se pudo determinar el tenant actual. Se procesarán todos los recursos.")

    print("--- Generador de Diagramas de Jerarquía de Azure para Draw.io ---")
    print(f"DEBUG: Argumentos recibidos:")
    print(f"  - diagram_mode: {args.diagram_mode}")
    print(f"  - output: {output_file}")
    print(f"  - include_ids: {args.include_ids}")
    print(f"  - exclude_ids: {args.exclude_ids}")
    print(f"  - tenant_filter: {args.tenant_filter}")
    print(f"  - all_tenants: {args.all_tenants}")
    print(f"  - no_embed_data: {args.no_embed_data}")
    print(f"  - input_json: {args.input_json}")
    print("")
    
    # Cargar datos según la fuente seleccionada
    if args.input_json:
        print(f"INFO: Cargando datos desde {args.input_json}")
        try:
            azure_items, dependencies = load_from_json_export(args.input_json)
            if not azure_items:
                print("ERROR: No se pudieron cargar los datos del archivo JSON.")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: Error al cargar datos del archivo JSON: {e}")
            sys.exit(1)
            
        # Aplicar filtrado por tenant a datos cargados desde JSON si se especifica
        if target_tenant:
            original_count = len(azure_items)
            azure_items = [item for item in azure_items if item.get('tenantId') == target_tenant]
            filtered_count = len(azure_items)
            if filtered_count != original_count:
                print(f"INFO: Filtrado por tenant {target_tenant}: {original_count} → {filtered_count} elementos")
    else:
        # Consultar Azure (con o sin cache)
        print("INFO: Consultando recursos de Azure...")
        use_cache = not args.no_cache
        try:
            azure_items = get_azure_resources(use_cache=use_cache, force_refresh=args.force_refresh, tenant_filter=target_tenant)
            if not azure_items:
                print("\nAVISO: No se encontraron elementos. Revisa tu login ('az login') y permisos.")
                sys.exit(0)
            print(f"INFO: Se encontraron {len(azure_items)} recursos")
            
            dependencies = find_dependencies(azure_items)
            print(f"INFO: Se encontraron {len(dependencies)} dependencias")
        except Exception as e:
            print(f"ERROR: Error al consultar recursos de Azure: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        # Exportar a JSON si se solicita
        if args.export_json:
            try:
                export_data = {
                    'metadata': {
                        'exported_at': __import__('datetime').datetime.now().isoformat(),
                        'total_items': len(azure_items),
                        'total_dependencies': len(dependencies)
                    },
                    'items': azure_items,
                    'dependencies': dependencies
                }
                
                with open(args.export_json, 'w', encoding='utf-8') as f:
                    __import__('json').dump(export_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Datos exportados a: {args.export_json}")
                
                # Si solo se quería exportar, terminar aquí
                if not args.diagram_mode:
                    sys.exit(0)
            except Exception as e:
                print(f"ERROR: Error al exportar datos JSON: {e}")
                sys.exit(1)
    
    # Filtrar si corresponde
    try:
        print("INFO: Aplicando filtros...")
        azure_items, dependencies = filter_items_and_dependencies(
            azure_items, dependencies, include_ids=args.include_ids, exclude_ids=args.exclude_ids)
        print(f"INFO: Después del filtrado: {len(azure_items)} recursos, {len(dependencies)} dependencias")
    except Exception as e:
        print(f"ERROR: Error al aplicar filtros: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Generar diagrama según el modo seleccionado
    try:
        print(f"INFO: Generando diagrama en modo '{args.diagram_mode}'...")
        drawio_content = generate_drawio_file(
            azure_items, dependencies, 
            embed_data=not args.no_embed_data, 
            include_ids=args.include_ids,
            diagram_mode=args.diagram_mode,
            no_hierarchy_edges=args.no_hierarchy_edges
        )
        print(f"INFO: Diagrama generado exitosamente")
    except Exception as e:
        print(f"ERROR: Error al generar diagrama: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Escribir archivo de salida
    try:
        # Crear el directorio de salida si no existe
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"INFO: Directorio creado: {output_dir}")
        
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(drawio_content)
        print(f"\n¡ÉXITO! Se ha creado el diagrama de '{args.diagram_mode}' en '{output_file}'.")
        
        if target_tenant:
            print(f"\nTenant filtrado: {target_tenant}")
        elif args.all_tenants:
            print(f"\nTodos los tenants incluidos (sin filtrado)")
            
        print(f"\nModo: {args.diagram_mode.upper()}")
        if args.diagram_mode == 'infrastructure':
            print("- Diagrama de jerarquía completa (Management Groups → Suscripciones → Resource Groups → Recursos)")
        elif args.diagram_mode == 'components':
            print("- Diagrama agrupado por función y tipo de recurso")
        elif args.diagram_mode == 'network':
            print("- Diagrama centrado en recursos de red y conectividad")
        elif args.diagram_mode == 'all':
            print("- Todos los diagramas en páginas separadas del mismo archivo")
            print("  • Página 1: Infrastructure (jerarquía completa)")
            print("  • Página 2: Components (agrupado por función)")
            print("  • Página 3: Network (recursos de red)")
            print("  • Página 4: Network (sin enlaces jerárquicos)")
        print("\n--- PRÓXIMOS PASOS ---")
        print("1. Abre el archivo en https://app.diagrams.net.")
        print("2. Organiza el diagrama: Selecciona todo (Ctrl+A) -> Menú 'Organizar' -> 'Disposición' -> 'Gráfico Jerárquico'.")
        print("\n3. Selecciona cualquier icono y presiona Ctrl+M (Cmd+M en Mac) para ver todos sus datos.")
    except IOError as e:
        print(f"\nERROR al escribir el archivo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

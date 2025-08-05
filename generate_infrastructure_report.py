#!/usr/bin/env python3
"""
Ejemplo de uso de la herramienta Azure Infrastructure Diagrams como módulo Python.
Este script demuestra cómo integrar la funcionalidad en aplicaciones personalizadas.
"""

import sys
import os
import json
from datetime import datetime

# Añadir el directorio src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from azure_api import get_azure_resources, find_dependencies, get_current_tenant_id
from drawio_export import generate_drawio_file, filter_items_and_dependencies

def generate_infrastructure_report(output_dir="reports", tenant_filter=None):
    """
    Genera un reporte completo de infraestructura Azure.
    
    Args:
        output_dir (str): Directorio de salida para los reportes
        tenant_filter (str): ID del tenant a filtrar (opcional)
    
    Returns:
        dict: Resumen del reporte generado
    """
    
    print("🚀 Iniciando generación de reporte de infraestructura Azure...")
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Obtener timestamp para archivos únicos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Obtener datos de Azure
    print("📊 Obteniendo recursos de Azure...")
    azure_items = get_azure_resources(use_cache=True, tenant_filter=tenant_filter)
    
    if not azure_items:
        print("❌ No se encontraron recursos de Azure")
        return None
    
    print(f"✅ Encontrados {len(azure_items)} recursos")
    
    # Encontrar dependencias
    print("🔗 Analizando dependencias...")
    dependencies = find_dependencies(azure_items)
    print(f"✅ Encontradas {len(dependencies)} dependencias")
    
    # Generar reportes en diferentes formatos
    reports = {}
    
    # 1. Diagrama completo (todos los modos)
    print("📈 Generando diagrama completo...")
    all_diagram_path = os.path.join(output_dir, f"azure_complete_{timestamp}.drawio")
    all_content = generate_drawio_file(
        azure_items, dependencies, 
        embed_data=True, 
        diagram_mode='all'
    )
    
    with open(all_diagram_path, 'w', encoding='utf-8') as f:
        f.write(all_content)
    
    reports['complete_diagram'] = all_diagram_path
    
    # 2. Diagrama de infraestructura (solo jerarquía)
    print("🏗️  Generando diagrama de infraestructura...")
    infra_diagram_path = os.path.join(output_dir, f"azure_infrastructure_{timestamp}.drawio")
    infra_content = generate_drawio_file(
        azure_items, dependencies, 
        embed_data=False,  # Datos mínimos para mejor rendimiento
        diagram_mode='infrastructure'
    )
    
    with open(infra_diagram_path, 'w', encoding='utf-8') as f:
        f.write(infra_content)
    
    reports['infrastructure_diagram'] = infra_diagram_path
    
    # 3. Diagrama de red
    print("🌐 Generando diagrama de red...")
    network_diagram_path = os.path.join(output_dir, f"azure_network_{timestamp}.drawio")
    network_content = generate_drawio_file(
        azure_items, dependencies, 
        embed_data=True, 
        diagram_mode='network',
        no_hierarchy_edges=True  # Solo dependencias funcionales
    )
    
    with open(network_diagram_path, 'w', encoding='utf-8') as f:
        f.write(network_content)
    
    reports['network_diagram'] = network_diagram_path
    
    # 4. Export JSON para análisis posterior
    print("💾 Exportando datos JSON...")
    json_export_path = os.path.join(output_dir, f"azure_inventory_{timestamp}.json")
    export_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'tenant_id': get_current_tenant_id() if not tenant_filter else tenant_filter,
            'total_resources': len(azure_items),
            'total_dependencies': len(dependencies),
            'generator': 'Azure Infrastructure Diagrams Script'
        },
        'resources': azure_items,
        'dependencies': dependencies,
        'summary': {
            'resource_types': get_resource_type_summary(azure_items),
            'locations': get_location_summary(azure_items),
            'subscriptions': get_subscription_summary(azure_items)
        }
    }
    
    with open(json_export_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    reports['json_export'] = json_export_path
    
    # 5. Generar reporte HTML summary
    print("📄 Generando reporte HTML...")
    html_report_path = os.path.join(output_dir, f"azure_report_{timestamp}.html")
    generate_html_report(export_data, html_report_path, reports)
    reports['html_report'] = html_report_path
    
    # Resumen final
    summary = {
        'timestamp': timestamp,
        'tenant_id': export_data['metadata']['tenant_id'],
        'total_resources': len(azure_items),
        'total_dependencies': len(dependencies),
        'files_generated': reports,
        'output_directory': output_dir
    }
    
    print(f"\n✅ Reporte generado exitosamente!")
    print(f"📁 Directorio: {output_dir}")
    print(f"📊 Recursos: {summary['total_resources']}")
    print(f"🔗 Dependencias: {summary['total_dependencies']}")
    print(f"📄 Archivos generados:")
    for report_type, path in reports.items():
        print(f"   - {report_type}: {os.path.basename(path)}")
    
    return summary

def get_resource_type_summary(azure_items):
    """Generar resumen por tipo de recurso"""
    type_counts = {}
    for item in azure_items:
        resource_type = item.get('type', 'unknown')
        type_counts[resource_type] = type_counts.get(resource_type, 0) + 1
    
    return dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True))

def get_location_summary(azure_items):
    """Generar resumen por ubicación"""
    location_counts = {}
    for item in azure_items:
        location = item.get('location', 'unknown')
        location_counts[location] = location_counts.get(location, 0) + 1
    
    return dict(sorted(location_counts.items(), key=lambda x: x[1], reverse=True))

def get_subscription_summary(azure_items):
    """Generar resumen por suscripción"""
    sub_counts = {}
    for item in azure_items:
        # Extraer subscription ID del resource ID
        resource_id = item.get('id', '')
        if '/subscriptions/' in resource_id:
            parts = resource_id.split('/subscriptions/')
            if len(parts) > 1:
                sub_id = parts[1].split('/')[0]
                sub_counts[sub_id] = sub_counts.get(sub_id, 0) + 1
    
    return dict(sorted(sub_counts.items(), key=lambda x: x[1], reverse=True))

def generate_html_report(export_data, html_path, diagram_files):
    """Generar reporte HTML con resumen ejecutivo"""
    
    metadata = export_data['metadata']
    summary = export_data['summary']
    
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Azure Infrastructure Report - {metadata['generated_at'][:10]}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #0078d4; border-bottom: 3px solid #0078d4; padding-bottom: 10px; }}
        h2 {{ color: #323130; margin-top: 30px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 6px; border-left: 4px solid #0078d4; }}
        .metric {{ font-size: 2em; font-weight: bold; color: #0078d4; }}
        .files-list {{ background: #f8f9fa; padding: 20px; border-radius: 6px; }}
        .files-list a {{ color: #0078d4; text-decoration: none; }}
        .files-list a:hover {{ text-decoration: underline; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; font-weight: 600; }}
        .badge {{ background: #0078d4; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏗️ Azure Infrastructure Report</h1>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="metric">{metadata['total_resources']}</div>
                <div>Total Resources</div>
            </div>
            <div class="summary-card">
                <div class="metric">{metadata['total_dependencies']}</div>
                <div>Dependencies</div>
            </div>
            <div class="summary-card">
                <div class="metric">{len(summary['resource_types'])}</div>
                <div>Resource Types</div>
            </div>
            <div class="summary-card">
                <div class="metric">{len(summary['locations'])}</div>
                <div>Azure Regions</div>
            </div>
        </div>
        
        <h2>📄 Generated Files</h2>
        <div class="files-list">
"""
    
    file_descriptions = {
        'complete_diagram': '🎯 Complete Diagram (All modes in single file)',
        'infrastructure_diagram': '🏗️ Infrastructure Hierarchy',
        'network_diagram': '🌐 Network Topology', 
        'json_export': '💾 Raw Data Export (JSON)',
        'html_report': '📊 This HTML Report'
    }
    
    for file_type, file_path in diagram_files.items():
        description = file_descriptions.get(file_type, file_type)
        filename = os.path.basename(file_path)
        html_content += f'            <div>• <strong>{description}</strong>: <a href="{filename}">{filename}</a></div>\n'
    
    html_content += f"""
        </div>
        
        <h2>📊 Resource Types</h2>
        <table>
            <thead>
                <tr><th>Resource Type</th><th>Count</th><th>Percentage</th></tr>
            </thead>
            <tbody>
"""
    
    total_resources = metadata['total_resources']
    for resource_type, count in list(summary['resource_types'].items())[:10]:  # Top 10
        percentage = (count / total_resources) * 100
        html_content += f'                <tr><td>{resource_type}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>\n'
    
    html_content += f"""
            </tbody>
        </table>
        
        <h2>🌍 Azure Regions</h2>
        <table>
            <thead>
                <tr><th>Region</th><th>Resources</th><th>Percentage</th></tr>
            </thead>
            <tbody>
"""
    
    for location, count in list(summary['locations'].items())[:10]:  # Top 10
        percentage = (count / total_resources) * 100
        html_content += f'                <tr><td>{location}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>\n'
    
    html_content += f"""
            </tbody>
        </table>
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 0.9em;">
            <p><strong>Generated:</strong> {metadata['generated_at']}</p>
            <p><strong>Tenant ID:</strong> {metadata['tenant_id']}</p>
            <p><strong>Generator:</strong> {metadata['generator']}</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate comprehensive Azure infrastructure reports")
    parser.add_argument('--output-dir', default='reports', help='Output directory for reports')
    parser.add_argument('--tenant-filter', help='Filter by specific tenant ID')
    
    args = parser.parse_args()
    
    try:
        summary = generate_infrastructure_report(
            output_dir=args.output_dir,
            tenant_filter=args.tenant_filter
        )
        
        if summary:
            print(f"\n🎉 Success! Report generated in: {summary['output_directory']}")
            print(f"📧 Share the HTML report: {os.path.basename(summary['files_generated']['html_report'])}")
        else:
            print("❌ Failed to generate report")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        sys.exit(1)

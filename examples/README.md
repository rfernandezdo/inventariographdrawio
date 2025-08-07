# Examples

Este directorio contiene scripts de ejemplo para uso avanzado de Azure Infrastructure Diagrams.

## 📁 Archivos Disponibles

### Integración y Análisis
- **`azure_to_drawio.py`** - Ejemplo de integración directa con las APIs
- **`demo_cache_workflow.py`** - Demuestra el flujo de trabajo con cache local  
- **`analyze_cache_and_create_masked_data.py`** - Análisis de cache y creación de datos enmascarados para testing

### Scripts de Uso Común
Para ejemplos de uso más comunes, ver:
- **`../generate_infrastructure_report.py`** - Script principal para reportes completos
- **`../EXAMPLES.md`** - 15+ ejemplos de configuración para GitHub Action y CLI

## 🚀 Uso

### Scripts Locales
```bash
# Desde el directorio raíz del proyecto:

# Demo del workflow de cache
python examples/demo_cache_workflow.py

# Analizar cache y crear datos enmascarados
python examples/analyze_cache_and_create_masked_data.py

# Reporte completo de infraestructura
python generate_infrastructure_report.py --output-dir reports
```

### GitHub Action
Para automatización, usar la GitHub Action directamente:
```yaml
- uses: rfernandezdo/inventariographdrawio@v2
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
    diagram-mode: 'all'
```

## 📚 Documentación

- **Setup de GitHub Action**: [../SETUP_GITHUB_ACTION.md](../SETUP_GITHUB_ACTION.md)
- **Ejemplos completos**: [../EXAMPLES.md](../EXAMPLES.md)
- **Documentación de la Action**: [../ACTION_README.md](../ACTION_README.md)

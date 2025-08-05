# Documentation

Este directorio contiene la documentación técnica del proyecto Azure Infrastructure Diagrams.

## 📖 Archivos de Documentación

### Core Documentation
- `DIAGRAM_MODES.md` - **Modos de diagrama**: Infrastructure, Components, Network, All
- `CACHE_LOCAL.md` - **Sistema de cache**: Optimización de rendimiento
- `DATOS_REALES.md` - **Manejo de datos**: Datos reales vs. enmascarados
- `TENANT_FILTERING.md` - **Filtrado multi-tenant**: Separación por tenant

### GitHub Action
- `../SETUP_GITHUB_ACTION.md` - **Configuración completa** de la GitHub Action
- `../ACTION_README.md` - **Documentación de uso** de la GitHub Action
- `../.github/workflows/` - **Ejemplos de workflows** listos para usar

### Desarrollo y Mejoras
- `COPILOT_INSTRUCTIONS.md` - **Instrucciones para GitHub Copilot**
- `COPILOT_CODE_EXAMPLES.md` - **Ejemplos de código** para desarrollo
- `IMPLEMENTATION_SUMMARY.md` - **Resumen de implementación** técnica general
- `GITHUB_ACTION_IMPLEMENTATION.md` - **Implementación específica** de GitHub Action
- `NETWORK_MODE_IMPROVEMENTS.md` - **Mejoras del modo Network**
- `Mejoras.md` - **Lista de mejoras** y funcionalidades pendientes

## 🎯 Organización por Tema

### 🤖 Automatización (GitHub Action)
Para usar el proyecto como GitHub Action para automatización CI/CD:
- Lee `../SETUP_GITHUB_ACTION.md` para configuración paso a paso
- Revisa `../.github/workflows/` para ejemplos de workflows
- Consulta `../ACTION_README.md` para referencia completa de parámetros

### 👨‍💻 Desarrollo Local
Para usar el proyecto como herramienta CLI local:
- `DIAGRAM_MODES.md` - Entiende los diferentes tipos de diagramas
- `CACHE_LOCAL.md` - Optimiza el rendimiento con cache
- `TENANT_FILTERING.md` - Maneja entornos multi-tenant

### 🏗️ Arquitectura y Datos
Para entender la arquitectura interna:
- `IMPLEMENTATION_SUMMARY.md` - Visión general del sistema
- `NETWORK_MODE_IMPROVEMENTS.md` - Arquitectura del modo Network
- `DATOS_REALES.md` - Seguridad y manejo de datos

### 🤖 Desarrollo con AI
Para desarrollo asistido por AI:
- `COPILOT_INSTRUCTIONS.md` - Instrucciones completas para GitHub Copilot
- `COPILOT_CODE_EXAMPLES.md` - Patrones de código y ejemplos

## 🚀 Quick Start

### Como GitHub Action (Recomendado)
```yaml
- uses: rfernandezdo/inventariographdrawio@v1
  with:
    azure-credentials: ${{ secrets.AZURE_CREDENTIALS }}
    diagram-mode: 'all'
    commit-changes: 'pr'
```

### Como CLI Local
```bash
python src/cli.py --diagram-mode all --output mi-diagrama.drawio
```

## 📊 Casos de Uso

- **📈 Informes automáticos**: Diagramas semanales vía GitHub Actions
- **🔍 Auditorías de arquitectura**: Visualización completa de infraestructura
- **📋 Documentación viva**: PRs automáticos con diagramas actualizados  
- **🏢 Multi-tenant**: Diagramas separados por organización/tenant
- **🌐 Análisis de red**: Topología y dependencias de conectividad

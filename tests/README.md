# Tests

Este directorio contiene todos los tests organizados por categorías:

## 📁 Estructura Organizada

### 🎨 Layout Tests (`layout/`)
Tests específicos para diferentes tipos de layout:
- `test_arc_*.py` - Tests para layout en arco (semicírculo)
- `test_grid_*.py` - Tests para layout en cuadrícula
- `test_radial_*.py` - Tests para layout radial (circular)
- `test_comparison_*.py` - Comparación entre diferentes layouts
- `test_edge_styles.py` - Tests para estilos de aristas (rectas vs ortogonales)
- `test_straight_edges*.py` - Tests específicos para líneas rectas

### 🔗 Integration Tests (`integration/`)
Tests de integración completa:
- `test_network_*.py` - Tests de redes complejas
- `test_modes.py` - Tests de diferentes modos de diagrama

### 🧪 Unit Tests (`unit/`)
Tests unitarios y básicos:
- `test_cache_*.py` - Tests del sistema de cache
- `test_simple.py` - Tests básicos de funcionalidad

### 🏗️ Hierarchy Tests (`hierarchy/`)
Tests principales de jerarquía y escalabilidad:
- `test_hierarchy.py` - Test principal de jerarquías
- `test_complex_tree.py` - Tests de árboles complejos
- `test_extensive_tree.py` - Tests de escalabilidad
- `test_super_extensive.py` - Tests de rendimiento

### 📋 Fixtures (`fixtures/`)
Archivos .drawio de ejemplo y resultado de tests:
- Diagramas de prueba generados
- Casos de ejemplo para validación visual

### 📊 Documentación
- `RESULTADOS_ESCALABILIDAD.md` - Resultados de tests de escalabilidad
- `README.md` - Este archivo

## 🚀 Cómo Ejecutar Tests

### Tests de Layout (Recomendado)
```bash
# Test principal de arco sin overlaps
python tests/layout/test_arc_no_overlap.py

# Test de layout en cuadrícula  
python tests/layout/test_grid_layout.py

# Comparación de layouts
python tests/layout/test_comparison_layouts.py
```

### Tests de Jerarquía
```bash
# Test principal
python tests/test_hierarchy.py

# Test complejo
python tests/test_complex_tree.py
```

### Tests de Integración
```bash
# Tests de red
python tests/integration/test_network_complete.py

# Tests de modos
python tests/integration/test_modes.py
```

## 🎯 Tests Principales Recomendados

1. **`layout/test_arc_no_overlap.py`** - Verificar layout en arco sin overlaps
2. **`test_hierarchy.py`** - Funcionalidad básica de jerarquías
3. **`test_complex_tree.py`** - Estructuras complejas
4. **`layout/test_comparison_layouts.py`** - Comparar diferentes layouts

## Ejecutar tests

Desde el directorio raíz del proyecto:

```bash
# Ejecutar un test específico
python3 tests/test_simple.py

# Ejecutar test de debug
python3 tests/test_debug.py

# Ejecutar test del sistema de cache
python3 tests/test_cache_system.py

# Ejecutar test de modos
python3 tests/test_modes.py

# Ejecutar test de red completo
python3 tests/test_network_complete.py
```

## Notas

Los archivos de test han sido actualizados para usar las rutas correctas después de la reorganización del proyecto.

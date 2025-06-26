# Tests

Este directorio contiene todos los archivos de prueba para el proyecto.

## Estructura

- `test_*.py` - Archivos de test individuales
- `fixtures/` - Archivos de datos de prueba (.drawio, etc.)
- `test_output.log` - Log de salida de los tests

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

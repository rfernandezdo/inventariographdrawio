# Data

Este directorio contiene archivos de datos del proyecto.

## Archivos

- `masked_realistic_inventory.json` - Datos enmascarados realistas para pruebas
- `azure_full_hierarchy_with_icons.drawio` - Diagrama completo de jerarquía Azure
- `azure_full_hierarchy_with_icons.drawio:Zone.Identifier` - Metadatos del archivo

## Uso

Los archivos de datos se utilizan en:

- Tests (datos enmascarados para pruebas)
- Ejemplos de diagramas
- Referencias de estructura

## Generación de datos

Para generar nuevos datos enmascarados:

```bash
python3 examples/analyze_cache_and_create_masked_data.py
```

## Notas

Los datos enmascarados no contienen información sensible real y pueden usarse de forma segura para pruebas y desarrollo.

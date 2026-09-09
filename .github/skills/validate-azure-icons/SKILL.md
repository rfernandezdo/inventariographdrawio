---
name: validate-azure-icons
description: 'Validate and extend the Azure icon library used by draw.io exports (src/drawio/icons.py, AZURE_ICONS dict) against a real local draw.io desktop installation. Use when: adding new Azure resource type -> icon mappings, fixing broken/missing icon paths, checking for duplicate AZURE_ICONS keys, or when asked to "completar/validar la libreria de iconos de azure drawio" reading a local drawio installation.'
---

# Validate Azure Icon Library

Compares `AZURE_ICONS` in [src/drawio/icons.py](../../../src/drawio/icons.py) against the real
SVG catalog bundled inside a local draw.io desktop installation, so icon paths referenced by
the generator are guaranteed to exist and render (not guessed from memory).

## When to Use

- User asks to complete/expand the Azure icon coverage for draw.io export.
- A generated `.drawio` file shows a broken/missing image for some resource type.
- Before adding new `AZURE_ICONS` entries, to confirm the exact local icon filename/category.
- Periodic maintenance check for duplicate keys or paths that no longer exist (e.g. after a
  draw.io desktop update renames/moves icon files).

## How draw.io stores icons locally

draw.io desktop ships all its bundled icons (`img/lib/azure2/...`, `img/lib/mscae/...`) inside
an Electron `app.asar` archive, typically at:

- Windows: `C:\Program Files\draw.io\resources\app.asar` (or `%LOCALAPPDATA%\Programs\draw.io\...`)
- macOS: `/Applications/draw.io.app/Contents/Resources/app.asar`
- Linux: `/opt/drawio/resources/app.asar`

`asar` is not a zip; list its contents with the `asar` npm package via `npx` (Node.js required):

```bash
npx --yes asar list "<path-to>/app.asar" | grep "img/lib/azure2"
```

## Procedure

1. Run the validator script: [validate_icon_library.py](./scripts/validate_icon_library.py)
   ```bash
   python .github/skills/validate-azure-icons/scripts/validate_icon_library.py
   # or, if draw.io isn't in a default location:
   python .github/skills/validate-azure-icons/scripts/validate_icon_library.py --drawio-path "D:\Apps\draw.io"
   ```
   It auto-detects common install paths, otherwise pass `--drawio-path` or set `DRAWIO_APP_PATH`.
2. Review the report: entries are bucketed as OK (verified locally), external (http URL, not
   verifiable), hidden (type is in `HIDDEN_RESOURCE_TYPES` so the icon is never actually used —
   safe to ignore), or broken (path does not exist in the local install — must fix), plus any
   duplicate dict keys.
3. To add new mappings: find the exact relative path with the `npx asar list | grep` command
   above (category folder + exact filename, case-sensitive), then add an entry to `AZURE_ICONS`
   as `"microsoft.<provider>/<type>": "img/lib/azure2/<category>/<Icon_Name>.svg"`.
4. Re-run the validator to confirm the new/changed entries resolve to `OK` and no duplicate keys
   were introduced (exit code `0` = pass, `1` = broken paths or duplicates found).

## Notes

- Prefer the modern `azure2` icon set over `mscae` (older, mostly superseded) unless `azure2` has
  no equivalent icon for that resource type.
- Never invent a filename — always confirm it exists in the `npx asar list` output first;
  singular/plural and category naming frequently changed between draw.io versions.
- The script requires Node.js/npx; the first run downloads the `asar` npm package (needs network).

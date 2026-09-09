#!/usr/bin/env python3
"""
Valida AZURE_ICONS (src/drawio/icons.py) contra el catalogo real de iconos
de una instalacion local de draw.io desktop (extraido de resources/app.asar).

Detecta:
  - Claves de tipo de recurso duplicadas en AZURE_ICONS.
  - Rutas de icono que no existen en el paquete app.asar local.
  - Entradas con URL externa (no verificables localmente).
  - Entradas de tipos marcados como "hidden" (HIDDEN_RESOURCE_TYPES), cuyo
    icono nunca se usa porque get_node_style() aplica antes el estilo hidden.

Requiere Node.js/npx disponible en PATH (usa "npx asar list" para listar el
contenido del .asar; en el primer uso descarga el paquete npm "asar").

Uso:
  python .github/skills/validate-azure-icons/scripts/validate_icon_library.py
  python .github/skills/validate-azure-icons/scripts/validate_icon_library.py --drawio-path "D:\\Apps\\draw.io"
  python .github/skills/validate-azure-icons/scripts/validate_icon_library.py --json
"""

import argparse
import collections
import json
import os
import re
import shutil
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
ICONS_FILE = os.path.join(REPO_ROOT, "src", "drawio", "icons.py")

# Rutas habituales de instalacion de draw.io desktop por sistema operativo
DEFAULT_DRAWIO_PATHS = [
    r"C:\Program Files\draw.io",
    r"C:\Program Files (x86)\draw.io",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\draw.io"),
    os.path.expandvars(r"%LOCALAPPDATA%\draw.io"),
    "/Applications/draw.io.app/Contents/Resources",
    "/opt/drawio/resources",
    "/usr/lib/draw.io/resources",
    "/usr/share/draw.io/resources",
]


def find_asar_path(explicit_path=None):
    """Localiza el archivo app.asar de draw.io, explicito o en rutas habituales."""
    candidates = []
    if explicit_path:
        candidates.append(explicit_path)
    candidates.extend(DEFAULT_DRAWIO_PATHS)

    for candidate in candidates:
        if not candidate:
            continue
        if candidate.endswith(".asar") and os.path.isfile(candidate):
            return candidate
        for sub in ("resources/app.asar", "app.asar"):
            path = os.path.join(candidate, sub)
            if os.path.isfile(path):
                return path
    return None


def list_asar_entries(asar_path):
    """Devuelve el listado de rutas dentro del .asar usando 'npx asar list'."""
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError(
            "No se encontro 'npx' en el PATH. Instala Node.js para poder listar "
            "el contenido de app.asar (https://nodejs.org)."
        )
    result = subprocess.run(
        [npx, "--yes", "asar", "list", asar_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"'npx asar list' fallo (codigo {result.returncode}).\n{result.stderr}"
        )
    return result.stdout.splitlines()


def normalize_entries(raw_entries):
    """Normaliza las rutas del asar a formato 'img/lib/...' en minusculas."""
    normalized = set()
    marker = "webapp/img/lib/"
    for line in raw_entries:
        line = line.strip().replace("\\", "/")
        idx = line.lower().find(marker)
        if idx != -1:
            normalized.add(line[idx + len("webapp/"):].lower())
    return normalized


def extract_azure_icons():
    """Importa AZURE_ICONS y HIDDEN_RESOURCE_TYPES desde el codigo fuente."""
    sys.path.insert(0, os.path.join(REPO_ROOT, "src"))
    from drawio.icons import AZURE_ICONS, HIDDEN_RESOURCE_TYPES
    return AZURE_ICONS, HIDDEN_RESOURCE_TYPES


def find_duplicate_keys():
    """Detecta claves de tipo de recurso repetidas en el fichero fuente."""
    with open(ICONS_FILE, encoding="utf-8") as f:
        text = f.read()
    keys = re.findall(r'^\s*"(microsoft\.[a-z0-9./]+)"\s*:', text, re.MULTILINE)
    counts = collections.Counter(keys)
    return sorted(key for key, count in counts.items() if count > 1)


def validate(asar_path):
    """Ejecuta la validacion completa y devuelve un dict con el resultado."""
    azure_icons, hidden_types = extract_azure_icons()
    duplicates = find_duplicate_keys()

    raw_entries = list_asar_entries(asar_path)
    available = normalize_entries(raw_entries)

    external, hidden, ok, broken = [], [], [], []
    for resource_type, icon_path in azure_icons.items():
        if icon_path.startswith("http"):
            external.append((resource_type, icon_path))
            continue
        if resource_type in hidden_types:
            hidden.append((resource_type, icon_path))
            continue
        if icon_path.lower() in available:
            ok.append((resource_type, icon_path))
        else:
            broken.append((resource_type, icon_path))

    return {
        "asar_path": asar_path,
        "total_entries": len(azure_icons),
        "duplicates": duplicates,
        "external": external,
        "hidden": hidden,
        "ok": ok,
        "broken": broken,
    }


def print_report(result):
    print("AZURE ICON LIBRARY VALIDATOR")
    print("=" * 60)
    print(f"Instalacion draw.io: {result['asar_path']}")
    print(f"Entradas en AZURE_ICONS: {result['total_entries']}")
    print(f"  OK (verificadas localmente): {len(result['ok'])}")
    print(f"  Externas (URL, no verificable): {len(result['external'])}")
    print(f"  Hidden (icono inalcanzable):    {len(result['hidden'])}")
    print(f"  Rotas (no existen localmente): {len(result['broken'])}")
    print(f"  Claves duplicadas:             {len(result['duplicates'])}")

    if result["duplicates"]:
        print("\nClaves duplicadas:")
        for key in result["duplicates"]:
            print(f"  - {key}")

    if result["broken"]:
        print("\nRutas rotas (no existen en el .asar local):")
        for resource_type, icon_path in result["broken"]:
            print(f"  - {resource_type} -> {icon_path}")

    print()
    if result["broken"] or result["duplicates"]:
        print("RESULTADO: FALLO")
    else:
        print("RESULTADO: OK")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--drawio-path", help="Ruta a la instalacion de draw.io o directamente a app.asar")
    parser.add_argument("--json", action="store_true", help="Imprime el resultado en formato JSON")
    args = parser.parse_args()

    explicit_path = args.drawio_path or os.environ.get("DRAWIO_APP_PATH")
    asar_path = find_asar_path(explicit_path)
    if not asar_path:
        print("ERROR: No se encontro app.asar de draw.io. Usa --drawio-path o la variable "
              "de entorno DRAWIO_APP_PATH para indicar la ruta de instalacion.", file=sys.stderr)
        sys.exit(2)

    try:
        result = validate(asar_path)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_report(result)

    sys.exit(1 if (result["broken"] or result["duplicates"]) else 0)


if __name__ == "__main__":
    main()

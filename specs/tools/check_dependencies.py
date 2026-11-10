#!/usr/bin/env python3
"""Inventario y comprobaciones de dependencias de SyntaxSprint.

Comprueba, sin red y sin dependencias externas:

- que ``requirements*.txt`` fijen versiones exactas y sin duplicados;
- que ``requirements-dev.txt`` incluya las de producción;
- que no haya dependencias de producción sin uso en el código;
- que la versión de Python coincida en ``.python-version``, Render y CI.

Uso:
    python specs/tools/check_dependencies.py
    python specs/tools/check_dependencies.py --strict
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "syntax_sprint"
PROD_FILE = ROOT / "requirements.txt"
DEV_FILE = ROOT / "requirements-dev.txt"
RUNTIME_FILE = ROOT / ".python-version"
RENDER_FILE = ROOT / "render.yaml"
CI_FILE = ROOT / ".github" / "workflows" / "ci.yml"

REQUIREMENT_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)"
    r"(?P<extras>\[[^\]]+\])?"
    r"==(?P<version>[^\s;#]+)"
    r"(?P<marker>\s*;.*)?$"
)
INCLUDE_RE = re.compile(r"^-r\s+(?P<path>\S+)$")

# Nombre de distribución -> módulo importable.
IMPORT_NAME = {
    "django": "django",
    "dj-database-url": "dj_database_url",
    "python-decouple": "decouple",
    "pylint-django": "pylint_django",
    "pip-audit": "pip_audit",
}

# Paquetes de producción que no se importan desde el código propio.
RUNTIME_ONLY = {
    "gunicorn": "se ejecuta como servidor WSGI",
    "psycopg": "lo carga el backend de PostgreSQL de Django",
}


def read_requirements(path: Path) -> tuple[list[tuple[str, str]], list[str], bool]:
    """Devuelve (dependencias, errores, incluye_produccion)."""
    dependencies: list[tuple[str, str]] = []
    errors: list[str] = []
    includes_prod = False
    if not path.exists():
        return dependencies, [f"no existe {path.relative_to(ROOT)}"], includes_prod

    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        include = INCLUDE_RE.match(line)
        if include:
            includes_prod = includes_prod or include.group("path") == PROD_FILE.name
            continue
        match = REQUIREMENT_RE.match(line)
        if not match:
            errors.append(f"{path.name}:{number}: no fija versión exacta: {line}")
            continue
        dependencies.append((match.group("name"), match.group("version")))
    return dependencies, errors, includes_prod


def find_duplicates(*groups: list[tuple[str, str]]) -> list[str]:
    """Devuelve las dependencias repetidas entre grupos."""
    seen: dict[str, int] = {}
    for group in groups:
        for name, _ in group:
            key = name.lower()
            seen[key] = seen.get(key, 0) + 1
    return [f"{name} aparece {count} veces" for name, count in sorted(seen.items()) if count > 1]


def source_text() -> str:
    """Concatena el código Python del proyecto para buscar imports."""
    chunks: list[str] = []
    for path in SOURCE_DIR.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def unused_production(dependencies: list[tuple[str, str]], text: str) -> list[str]:
    """Devuelve las dependencias de producción sin referencia en el código."""
    unused: list[str] = []
    for name, _ in dependencies:
        key = name.lower()
        if key in RUNTIME_ONLY:
            continue
        module = IMPORT_NAME.get(key, key.replace("-", "_"))
        pattern = rf"(?<![\w.]){re.escape(module)}(?![\w])"
        if not re.search(pattern, text):
            unused.append(name)
    return unused


def declared_python() -> tuple[str | None, list[str]]:
    """Comprueba que la versión de Python sea la misma en todo el proyecto."""
    errors: list[str] = []
    if not RUNTIME_FILE.exists():
        return None, ["falta .python-version"]

    lines = [line.strip() for line in RUNTIME_FILE.read_text(encoding="utf-8").splitlines()]
    version = next((line for line in lines if line), None)
    if not version:
        return None, [".python-version está vacío"]

    render = RENDER_FILE.read_text(encoding="utf-8")
    render_version = next_python_version(render)
    if render_version is None:
        errors.append("render.yaml no declara PYTHON_VERSION")
    elif render_version != version:
        errors.append(f"render.yaml usa {render_version} y .python-version {version}")

    ci = CI_FILE.read_text(encoding="utf-8")
    file_match = re.search(r'python-version-file:\s*"?([^"\s]+)"?', ci)
    if file_match:
        declared = file_match.group(1).removeprefix("./")
        if declared != RUNTIME_FILE.name:
            errors.append(f"el CI lee {declared} y se esperaba {RUNTIME_FILE.name}")
    else:
        version_match = re.search(r'python-version:\s*"?([0-9][0-9.]*)"?', ci)
        if not version_match:
            errors.append("el CI no declara la versión de Python")
        elif version_match.group(1) != version:
            errors.append(f"el CI usa {version_match.group(1)} y .python-version {version}")
    return version, errors


def next_python_version(config: str) -> str | None:
    """Lee el ``value`` que sigue a ``PYTHON_VERSION`` en un YAML."""
    lines = config.splitlines()
    for index, line in enumerate(lines):
        if "PYTHON_VERSION" not in line:
            continue
        for following in lines[index + 1 : index + 6]:
            match = re.search(r'value:\s*"?([0-9][0-9.]*)"?', following)
            if match:
                return match.group(1)
    return None


def main() -> int:
    """Ejecuta las comprobaciones y devuelve el código de salida."""
    parser = argparse.ArgumentParser(description="Comprueba las dependencias del proyecto.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="falla también si hay dependencias de producción sin uso",
    )
    args = parser.parse_args()

    print("== Inventario ==")
    production, errors, _ = read_requirements(PROD_FILE)
    development, dev_errors, includes_prod = read_requirements(DEV_FILE)
    errors.extend(dev_errors)
    if not includes_prod:
        errors.append("requirements-dev.txt no incluye -r requirements.txt")

    print(f"Producción: {len(production)} dependencias")
    print(f"Desarrollo: {len(development)} dependencias adicionales")

    duplicates = find_duplicates(production, development)
    errors.extend(duplicates)
    print(f"Duplicadas: {len(duplicates)}")

    print("\n== Uso en el código ==")
    unused = unused_production(production, source_text())
    if unused:
        for name in unused:
            print(f"Sin uso: {name}")
        if args.strict:
            errors.extend(f"dependencia de producción sin uso: {name}" for name in unused)
    else:
        print("Sin uso: ninguna")
    for name, reason in sorted(RUNTIME_ONLY.items()):
        print(f"Exenta: {name} ({reason})")

    print("\n== Runtime ==")
    python_version, runtime_errors = declared_python()
    errors.extend(runtime_errors)
    print(f".python-version: {python_version or 'desconocida'}")

    print("\n== Resultado ==")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

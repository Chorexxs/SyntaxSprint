#!/usr/bin/env python3
"""Escáner de secretos y datos sensibles para SyntaxSprint.

Uso:
    python specs/tools/scan_secrets.py
    python specs/tools/scan_secrets.py --history
    python specs/tools/scan_secrets.py --json

Reglas de seguridad:
- Nunca imprime el valor del secreto: solo patrón, archivo y línea.
- Código de salida 1 si hay hallazgos CRITICA o ALTA.
- Solo analiza archivos rastreados por git (y el historial con --history).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]

SKIP_SUFFIXES = {
    ".pyc", ".pyo", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp",
    ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".zip", ".gz", ".pdf",
    ".sqlite", ".sqlite3", ".db", ".bin",
}
SKIP_DIRS = {".git", "venv", ".venv", "node_modules", "__pycache__", ".agents"}
MAX_BYTES = 1_000_000

SEVERITY_ORDER = {"CRITICA": 0, "ALTA": 1, "MEDIA": 2, "BAJA": 3}

SENSITIVE_NAMES = [
    (re.compile(r"(^|/)\.env$", re.IGNORECASE), "Archivo .env versionado", "CRITICA"),
    (re.compile(r"\.(sqlite3?|db)$", re.IGNORECASE), "Base de datos versionada", "CRITICA"),
    (re.compile(r"\.(pem|key|p12|pfx|jks)$", re.IGNORECASE), "Clave o certificado versionado", "ALTA"),
    (re.compile(r"(^|/)(id_rsa|id_ed25519|id_dsa)$", re.IGNORECASE), "Clave privada SSH", "CRITICA"),
    (re.compile(r"\.(pyc|pyo)$", re.IGNORECASE), "Bytecode compilado versionado", "BAJA"),
    (re.compile(r"\.log$", re.IGNORECASE), "Archivo de log versionado", "MEDIA"),
]

PATTERNS = [
    ("SECRET_KEY asignada en código",
     re.compile(r"(?i)(secret[_-]?key|django_secret_key)\s*[:=]\s*['\"][^'\"]{8,}"), "CRITICA"),
    ("Contraseña hardcodeada",
     re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{4,}['\"]"), "ALTA"),
    ("API key o token genérico",
     re.compile(r"(?i)(api[_-]?key|apikey|access[_-]?token|auth[_-]?token|"
                r"client[_-]?secret)\s*[:=]\s*['\"][^'\"]{8,}"), "ALTA"),
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}"), "CRITICA"),
    ("GitHub Token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "CRITICA"),
    ("Slack Token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "CRITICA"),
    ("Stripe Live Key", re.compile(r"sk_live_[A-Za-z0-9]{16,}"), "CRITICA"),
    ("Google API Key", re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "ALTA"),
    ("Clave privada PEM",
     re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "CRITICA"),
    ("Bearer token", re.compile(r"(?i)bearer\s+[A-Za-z0-9\-_.]{20,}"), "ALTA"),
    ("URL con credenciales",
     re.compile(r"(?i)\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@"), "ALTA"),
    ("JWT", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "MEDIA"),
    ("DEBUG activo en código", re.compile(r"(?m)^\s*DEBUG\s*=\s*True\b"), "ALTA"),
    ("ALLOWED_HOSTS comodín",
     re.compile(r"ALLOWED_HOSTS\s*=\s*\[\s*['\"]\*['\"]"), "ALTA"),
]


def git(*args: str) -> str:
    """Ejecuta git desde la raíz del repositorio."""
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, errors="replace"
    )
    return result.stdout


def tracked_files() -> list[str]:
    """Devuelve las rutas rastreadas por git."""
    return [line.strip() for line in git("ls-files").splitlines() if line.strip()]


def should_skip(path: str) -> bool:
    """Indica si un archivo debe omitirse del análisis de contenido."""
    parts = Path(path).parts
    if any(part in SKIP_DIRS for part in parts):
        return True
    return Path(path).suffix.lower() in SKIP_SUFFIXES


def iter_lines(path: str) -> Iterable[tuple[int, str]]:
    """Itera líneas de un archivo de texto de forma segura."""
    full = ROOT / path
    try:
        if full.stat().st_size > MAX_BYTES:
            return
        raw = full.read_bytes()
        if b"\x00" in raw[:1024]:
            return
        text = raw.decode("utf-8", errors="replace")
    except (OSError, UnicodeError):
        return
    for number, line in enumerate(text.splitlines(), start=1):
        yield number, line


def scan_names(files: list[str]) -> list[dict]:
    """Detecta nombres de archivo sensibles rastreados."""
    findings = []
    for path in files:
        for regex, label, severity in SENSITIVE_NAMES:
            if regex.search(path):
                findings.append({
                    "tipo": "archivo",
                    "patron": label,
                    "archivo": path,
                    "linea": 0,
                    "severidad": severity,
                })
    return findings


def scan_content(files: list[str]) -> list[dict]:
    """Busca patrones de secretos en el contenido de los archivos."""
    findings = []
    for path in files:
        if should_skip(path):
            continue
        for number, line in iter_lines(path):
            for label, regex, severity in PATTERNS:
                if regex.search(line):
                    findings.append({
                        "tipo": "contenido",
                        "patron": label,
                        "archivo": path,
                        "linea": number,
                        "severidad": severity,
                    })
    return findings


def scan_history(max_commits: int = 200) -> list[dict]:
    """Busca patrones en las líneas añadidas del historial de git."""
    output = git(
        "log", "--all", "-p", "--no-color", "--unified=0", f"-n{max_commits}"
    )
    findings = []
    current_file = "(desconocido)"
    current_commit = "(desconocido)"
    for line in output.splitlines():
        if line.startswith("commit "):
            current_commit = line.split()[1]
        elif line.startswith("+++ b/"):
            current_file = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            added = line[1:]
            for label, regex, severity in PATTERNS:
                if regex.search(added):
                    findings.append({
                        "tipo": "historial",
                        "patron": label,
                        "archivo": current_file,
                        "linea": 0,
                        "commit": current_commit,
                        "severidad": severity,
                    })
    return findings


def dedupe(findings: list[dict]) -> list[dict]:
    """Elimina hallazgos duplicados preservando el orden."""
    seen = set()
    unique = []
    for item in findings:
        key = (
            item["patron"], item["archivo"], item["linea"],
            item["tipo"], item.get("commit", ""),
        )
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def render(findings: list[dict]) -> None:
    """Imprime el informe en texto plano sin revelar valores."""
    if not findings:
        print("Sin hallazgos de secretos ni archivos sensibles.")
        return
    for item in findings:
        location = item["archivo"]
        if item["linea"]:
            location = f"{location}:{item['linea']}"
        if item.get("commit"):
            location = f"{location} @{item['commit'][:8]}"
        print(f"[{item['severidad']}] {item['patron']} -> {location} ({item['tipo']})")

    print("\nResumen por severidad:")
    for severity in SEVERITY_ORDER:
        count = sum(1 for item in findings if item["severidad"] == severity)
        if count:
            print(f"  {severity}: {count}")


def main() -> int:
    """Punto de entrada del escáner."""
    parser = argparse.ArgumentParser(description="Escáner de secretos de SyntaxSprint")
    parser.add_argument("--history", action="store_true", help="analizar historial de git")
    parser.add_argument("--json", action="store_true", help="salida en JSON")
    parser.add_argument("--max-commits", type=int, default=200,
                        help="commits a revisar en el historial (default: 200)")
    args = parser.parse_args()

    files = tracked_files()
    findings = scan_names(files) + scan_content(files)
    if args.history:
        findings += scan_history(args.max_commits)
    findings = dedupe(findings)
    findings.sort(key=lambda item: (SEVERITY_ORDER[item["severidad"]], item["archivo"]))

    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        render(findings)

    blocking = any(item["severidad"] in ("CRITICA", "ALTA") for item in findings)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())

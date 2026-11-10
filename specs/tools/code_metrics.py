#!/usr/bin/env python3
"""Métricas de calidad y escalabilidad del código de SyntaxSprint.

Uso:
    python specs/tools/code_metrics.py
    python specs/tools/code_metrics.py --path syntax_sprint --json

Mide complejidad, longitud de funciones, anidamiento, imports y malas prácticas
básicas en Python, además de señales de riesgo en JavaScript.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_FUNCTION_LINES = 40
MAX_COMPLEXITY = 10
MAX_NESTING = 4
MAX_PARAMS = 5
MAX_LINE_LENGTH = 100

CONTROL_NODES = (
    ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With,
    ast.AsyncWith, ast.IfExp, ast.BoolOp, ast.ExceptHandler,
)
COMPREHENSIONS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)

JS_RISK_PATTERNS = [
    (re.compile(r"\beval\s*\("), "Uso de eval()"),
    (re.compile(r"\.innerHTML\s*="), "Asignación a innerHTML (riesgo XSS)"),
    (re.compile(r"document\.write\s*\("), "Uso de document.write()"),
    (re.compile(r"\bvar\s+"), "Uso de var en lugar de let/const"),
    (re.compile(r"(?<![=!])==(?!=)"), "Comparación con == en lugar de ==="),
    (re.compile(r"console\.(log|debug)\s*\("), "console.log en código de producción"),
]


@dataclass
class FunctionMetric:
    """Métricas de una función o método."""

    name: str
    line: int
    lines: int
    complexity: int
    max_depth: int
    params: int
    typed: bool


@dataclass
class FileMetric:
    """Métricas agregadas de un archivo."""

    path: str
    loc: int
    blank: int
    comment: int
    functions: list[FunctionMetric] = field(default_factory=list)
    long_lines: int = 0
    todos: int = 0
    bare_except: int = 0
    broad_except: int = 0
    prints: int = 0
    max_nesting: int = 0
    js_findings: list[dict] = field(default_factory=list)


def iter_python_files(base: Path) -> list[Path]:
    """Lista archivos .py omitiendo entornos y bytecode."""
    return sorted(
        path for path in base.rglob("*.py")
        if not any(part in {".git", "venv", "__pycache__", ".agents"}
                   for part in path.parts)
    )


def iter_text_files(base: Path, suffix: str) -> list[Path]:
    """Lista archivos de texto por extensión, omitiendo entornos."""
    return sorted(
        path for path in base.rglob(f"*{suffix}")
        if not any(part in {".git", "venv", "__pycache__", ".agents"}
                   for part in path.parts)
    )


def node_complexity(node: ast.AST) -> int:
    """Aproxima la complejidad ciclomática de un nodo."""
    total = 1
    for child in ast.walk(node):
        if isinstance(child, CONTROL_NODES):
            total += 1
        elif isinstance(child, COMPREHENSIONS):
            total += len(child.generators)
    return total


def node_depth(node: ast.AST, depth: int = 0) -> int:
    """Calcula la profundidad máxima de estructuras de control."""
    deepest = depth
    for child in ast.iter_child_nodes(node):
        step = 1 if isinstance(child, CONTROL_NODES + COMPREHENSIONS) else 0
        deepest = max(deepest, node_depth(child, depth + step))
    return deepest


def has_type_hints(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Indica si la firma tiene anotaciones de tipo relevantes."""
    args = [*node.args.args, *node.args.kwonlyargs]
    if any(arg.annotation is not None for arg in args):
        return True
    return node.returns is not None


def analyze_python(path: Path) -> FileMetric | None:
    """Analiza un archivo Python y devuelve sus métricas."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return None

    lines = source.splitlines()
    metric = FileMetric(
        path=str(path.relative_to(ROOT)),
        loc=sum(1 for line in lines if line.strip()),
        blank=sum(1 for line in lines if not line.strip()),
        comment=sum(1 for line in lines if line.strip().startswith("#")),
    )

    for number, line in enumerate(lines, start=1):
        if len(line) > MAX_LINE_LENGTH:
            metric.long_lines += 1
        if re.search(r"\b(TODO|FIXME|HACK|XXX)\b", line):
            metric.todos += 1

    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"):
            metric.prints += 1
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                metric.bare_except += 1
            elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                metric.broad_except += 1

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            function = FunctionMetric(
                name=node.name,
                line=node.lineno,
                lines=end - node.lineno + 1,
                complexity=node_complexity(node),
                max_depth=node_depth(node),
                params=len(node.args.args) + len(node.args.kwonlyargs),
                typed=has_type_hints(node),
            )
            metric.functions.append(function)
            metric.max_nesting = max(metric.max_nesting, function.max_depth)

    return metric


def analyze_javascript(path: Path) -> FileMetric:
    """Analiza señales de riesgo básicas en un archivo JavaScript."""
    source = path.read_text(encoding="utf-8", errors="replace")
    lines = source.splitlines()
    metric = FileMetric(
        path=str(path.relative_to(ROOT)),
        loc=sum(1 for line in lines if line.strip()),
        blank=sum(1 for line in lines if not line.strip()),
        comment=sum(1 for line in lines if line.strip().startswith("//")),
    )
    metric.long_lines = sum(1 for line in lines if len(line) > MAX_LINE_LENGTH)
    for number, line in enumerate(lines, start=1):
        for regex, label in JS_RISK_PATTERNS:
            if regex.search(line):
                metric.js_findings.append({"line": number, "riesgo": label})
    return metric


def render(metrics: list[FileMetric]) -> None:
    """Imprime un informe legible."""
    total_functions = sum(len(item.functions) for item in metrics)
    total_loc = sum(item.loc for item in metrics)
    print(f"Archivos analizados: {len(metrics)}")
    print(f"Líneas de código: {total_loc} | Funciones: {total_functions}")

    print("\nComplejidad / longitud fuera de umbral:")
    flagged = 0
    for metric in metrics:
        for function in metric.functions:
            reasons = []
            if function.complexity > MAX_COMPLEXITY:
                reasons.append(f"complejidad {function.complexity}")
            if function.lines > MAX_FUNCTION_LINES:
                reasons.append(f"{function.lines} líneas")
            if function.max_depth > MAX_NESTING:
                reasons.append(f"anidamiento {function.max_depth}")
            if function.params > MAX_PARAMS:
                reasons.append(f"{function.params} parámetros")
            if reasons:
                flagged += 1
                print(f"  {metric.path}:{function.line} {function.name} -> "
                      + ", ".join(reasons))
    if not flagged:
        print("  Sin funciones fuera de umbral.")

    print("\nSeñales por archivo:")
    for metric in metrics:
        signals = []
        if metric.long_lines:
            signals.append(f"{metric.long_lines} líneas largas")
        if metric.todos:
            signals.append(f"{metric.todos} TODO/FIXME")
        if metric.bare_except:
            signals.append(f"{metric.bare_except} except desnudo")
        if metric.broad_except:
            signals.append(f"{metric.broad_except} except Exception")
        if metric.prints:
            signals.append(f"{metric.prints} print()")
        if metric.js_findings:
            signals.append(f"{len(metric.js_findings)} riesgos JS")
        if signals:
            print(f"  {metric.path}: " + ", ".join(signals))

    untyped = [item for item in metrics for fn in item.functions if not fn.typed]
    print(f"\nFunciones sin anotaciones de tipo: {len(untyped)}")


def main() -> int:
    """Punto de entrada del medidor."""
    parser = argparse.ArgumentParser(description="Métricas de código de SyntaxSprint")
    parser.add_argument("--path", default="syntax_sprint", help="directorio a analizar")
    parser.add_argument("--json", action="store_true", help="salida en JSON")
    args = parser.parse_args()

    base = (ROOT / args.path).resolve()
    metrics: list[FileMetric] = []
    for path in iter_python_files(base):
        analysis = analyze_python(path)
        if analysis is not None:
            metrics.append(analysis)
    for path in iter_text_files(base, ".js"):
        metrics.append(analyze_javascript(path))

    if args.json:
        print(json.dumps([asdict(item) for item in metrics], ensure_ascii=False, indent=2))
    else:
        render(metrics)
    return 0


if __name__ == "__main__":
    sys.exit(main())

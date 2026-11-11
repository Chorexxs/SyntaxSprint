"""Informe de métricas de producto (spec 011)."""

from __future__ import annotations

from typing import Any

from django.core.management.base import (BaseCommand, CommandError,
                                         CommandParser)

from ...analytics import DEFAULT_WINDOW_DAYS, build_report


def _format(value: float | None, suffix: str = "") -> str:
    """Formatea una métrica opcional."""
    return "sin datos" if value is None else f"{value:.2f}{suffix}"


class Command(BaseCommand):
    help = "Muestra las métricas de éxito del producto para una ventana de días."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--days",
            type=int,
            default=DEFAULT_WINDOW_DAYS,
            help="Días de la ventana de análisis (por defecto 28).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        days = options["days"]
        if days < 1:
            raise CommandError("--days debe ser mayor o igual que 1")
        report = build_report(days)
        self.stdout.write(f"== Analítica (últimos {report['days']} días) ==")

        if (
            report["events"] == 0
            and report["error_rate"] is None
            and report["tests_per_user_week"] is None
            and report["share_with_results"] is None
        ):
            self.stdout.write("sin datos en la ventana")
            return

        self.stdout.write(
            "Tests por usuario activo y semana .. "
            f"{_format(report['tests_per_user_week'])}  (objetivo >= 3)"
        )
        self.stdout.write(
            "Error rate de /get_python_function .. "
            f"{_format(report['error_rate'], ' %')}  (objetivo < 1 %)"
        )
        self.stdout.write(
            "Usuarios con al menos un resultado .. "
            f"{_format(report['share_with_results'], ' %')}  (objetivo >= 60 %)"
        )
        self.stdout.write(f"Eventos de fragmentos .............. {report['events']}")
        self.stdout.write(
            "Lighthouse ......................... "
            "se mide con Lighthouse CLI sobre la portada"
        )

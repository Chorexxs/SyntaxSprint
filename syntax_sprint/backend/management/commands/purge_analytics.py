"""Purga de eventos de analítica por retención (spec 011)."""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from ...analytics import DEFAULT_RETENTION_DAYS, purge_snippet_requests


class Command(BaseCommand):
    help = "Elimina los eventos de fragmentos anteriores a la retención indicada."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--days",
            type=int,
            default=DEFAULT_RETENTION_DAYS,
            help="Días de retención (por defecto 90).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        deleted = purge_snippet_requests(options["days"])
        self.stdout.write(f"{deleted} eventos eliminados")

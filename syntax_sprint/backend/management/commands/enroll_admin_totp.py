"""Enrolamiento TOTP del admin (spec 012)."""

from __future__ import annotations

import os
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import (BaseCommand, CommandError,
                                         CommandParser)

from ...models import AdminTOTP
from ...totp import generate_secret, provisioning_uri


def write_secret_file(path: str, username: str, secret: str) -> None:
    """Escribe secreto y URI en un archivo legible solo por su propietario."""
    content = (
        f"Secreto TOTP para {username}: {secret}\n"
        f"URI: {provisioning_uri(secret, username)}\n"
    )
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(content)
    if os.name == "posix":
        os.chmod(path, 0o600)


class Command(BaseCommand):
    help = "Enrola, rota o desactiva el TOTP de un usuario staff."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--username", required=True, help="Usuario staff.")
        parser.add_argument(
            "--disable",
            action="store_true",
            help="Elimina el dispositivo en lugar de crearlo.",
        )
        parser.add_argument(
            "--write",
            metavar="ARCHIVO",
            help="Guarda secreto y URI en ARCHIVO (0600) en lugar de imprimirlos.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        username = options["username"]
        user = get_user_model().objects.filter(username=username, is_staff=True).first()
        if user is None:
            raise CommandError("No existe un usuario staff con ese username")

        if options["disable"]:
            deleted, _ = AdminTOTP.objects.filter(user=user).delete()
            self.stdout.write(
                f"TOTP desactivado para {user.username} ({deleted} registro(s))"
            )
            return

        secret = generate_secret()
        device, created = AdminTOTP.objects.get_or_create(
            user=user,
            defaults={"secret": secret, "confirmed": True, "last_counter": 0},
        )
        if not created:
            device.secret = secret
            device.confirmed = True
            device.last_counter = 0
            device.version += 1
            device.save(
                update_fields=["secret", "confirmed", "last_counter", "version"]
            )
        destination = options.get("write")
        if destination:
            try:
                write_secret_file(destination, user.username, secret)
            except OSError as exc:
                raise CommandError(
                    f"No se pudo escribir {destination}: {exc}"
                ) from exc
            self.stdout.write(
                f"Secreto y URI guardados en {destination} (permisos 0600)."
            )
            self.stdout.write("Bórralo después de añadirlo a la app de autenticación.")
        else:
            self.stdout.write(
                "Secreto generado, pero no se imprime para no dejarlo en los logs."
            )
            self.stdout.write("Repite con --write <archivo> para guardarlo.")

"""Enrolamiento TOTP del admin (spec 012)."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import (BaseCommand, CommandError,
                                         CommandParser)

from ...models import AdminTOTP
from ...totp import generate_secret, provisioning_uri


class Command(BaseCommand):
    help = "Enrola, rota o desactiva el TOTP de un usuario staff."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--username", required=True, help="Usuario staff.")
        parser.add_argument(
            "--disable",
            action="store_true",
            help="Elimina el dispositivo en lugar de crearlo.",
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
        self.stdout.write(f"Secreto TOTP para {user.username}: {secret}")
        self.stdout.write(f"URI: {provisioning_uri(secret, user.username)}")
        self.stdout.write("Añádelo a tu app de autenticación y limpia la terminal.")

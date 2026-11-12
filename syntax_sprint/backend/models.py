"""Modelos de datos de SyntaxSprint."""

from django.conf import settings
from django.db import models


class TypingTestResult(models.Model):
    """Resultado de un test de mecanografía."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wpm = models.FloatField()
    accuracy = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.wpm} WPM, {self.accuracy}% Accuracy"


class SnippetRequest(models.Model):
    """Petición atendida por el servicio de fragmentos (analítica, spec 011)."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    language = models.CharField(max_length=32)
    status_code = models.PositiveSmallIntegerField(db_index=True)
    duration_ms = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.language} {self.status_code} ({self.duration_ms} ms)"


class AdminTOTP(models.Model):
    """Dispositivo TOTP de un administrador (spec 012)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_totp",
    )
    secret = models.CharField(max_length=32)
    confirmed = models.BooleanField(default=False)
    last_counter = models.BigIntegerField(default=0)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"TOTP de {self.user.username}"

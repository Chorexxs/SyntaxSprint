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

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class TypingTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wpm = models.FloatField()
    accuracy = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.wpm} WPM, {self.accuracy}% Accuracy"

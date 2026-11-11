"""Registro de modelos en el admin de Django."""

from django.contrib import admin

from .models import TypingTestResult


@admin.register(TypingTestResult)
class TypingTestResultAdmin(admin.ModelAdmin):
    """Administración de resultados de tests."""

    list_display = ("user", "wpm", "accuracy", "date")
    list_filter = ("date", "user")
    search_fields = ("user__username", "user__email")
    ordering = ("-date",)
    date_hierarchy = "date"

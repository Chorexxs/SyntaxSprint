"""Registro de modelos en el admin de Django."""

from django.contrib import admin
from django.http import HttpRequest

from .models import SnippetRequest, TypingTestResult


@admin.register(TypingTestResult)
class TypingTestResultAdmin(admin.ModelAdmin):
    """Administración de resultados de tests."""

    list_display = ("user", "wpm", "accuracy", "date")
    list_filter = ("date", "user")
    search_fields = ("user__username", "user__email")
    ordering = ("-date",)
    date_hierarchy = "date"


@admin.register(SnippetRequest)
class SnippetRequestAdmin(admin.ModelAdmin):
    """Consulta de eventos de analítica en solo lectura."""

    list_display = ("created_at", "language", "status_code", "duration_ms")
    list_filter = ("status_code", "language")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

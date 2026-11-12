"""Pruebas del rate limiting y de la caché compartida."""

from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

PASSWORD = "".join(("Str0ng", "-Pass!2026"))
User = get_user_model()


class CacheConfigTests(TestCase):
    """Configuración de la caché del rate limiting."""

    def test_shared_cache_backend_is_database(self):
        self.assertIn("DatabaseCache", settings.CACHES["shared"]["BACKEND"])

    def test_default_alias_is_local(self):
        self.assertEqual(settings.RATE_LIMIT_CACHE_ALIAS, "default")


class RateLimitTests(TestCase):
    """Límites del endpoint de fragmentos y del login del admin."""

    def setUp(self):
        cache.clear()

    def test_snippet_endpoint_returns_429_after_limit(self):
        with mock.patch("backend.snippet_views.SNIPPET_LIMIT", 2):
            first = self.client.get(reverse("get_python_function"))
            second = self.client.get(reverse("get_python_function"))
            third = self.client.get(reverse("get_python_function"))

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(third.status_code, 429)
        self.assertEqual(third.json()["error"], "Demasiadas peticiones")

    def test_admin_login_returns_429_after_limit(self):
        for _ in range(5):
            response = self.client.post(
                "/admin/login/", {"username": "x", "password": "y"}
            )
            self.assertNotEqual(response.status_code, 429)

        blocked = self.client.post("/admin/login/", {"username": "x", "password": "y"})

        self.assertEqual(blocked.status_code, 429)
        self.assertIn("Demasiados intentos", blocked.content.decode())

    def test_admin_successful_login_resets_counter(self):
        User.objects.create_superuser(
            username="admin", email="admin@example.com", password=PASSWORD
        )
        for _ in range(4):
            self.client.post(
                "/admin/login/", {"username": "admin", "password": "incorrecta"}
            )

        response = self.client.post(
            "/admin/login/", {"username": "admin", "password": PASSWORD}
        )

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(cache.get("ratelimit:admin-login:127.0.0.1"))

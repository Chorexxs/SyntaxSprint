"""Pruebas de seguridad y comportamiento de SyntaxSprint."""

import json
import os
import tempfile
from datetime import timedelta
from io import StringIO
from pathlib import Path
from unittest import mock, skipUnless

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import DatabaseError, connection
from django.test import Client, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from .analytics import (PURGE_CACHE_KEY, share_of_users_with_results,
                        snippet_error_rate, tests_per_active_user_per_week)
from .models import AdminTOTP, SnippetRequest, TypingTestResult
from .ratelimit import ADMIN_2FA_LIMIT
from .snippets import CODE_SNIPPETS, validate_catalog
from .totp import code_for_counter, current_counter, generate_secret
from .two_factor import SESSION_KEY, VERSION_KEY

PASSWORD = "".join(("Str0ng", "-Pass!2026"))
User = get_user_model()


class AuthTests(TestCase):
    """Registro, login, logout y rutas protegidas."""

    def setUp(self):
        cache.clear()

    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "tester",
                "email": "tester@example.com",
                "password": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(User.objects.filter(username="tester").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_signup_missing_fields_returns_400(self):
        response = self.client.post(reverse("signup"), {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)

    def test_signup_rejects_password_mismatch(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "tester",
                "email": "tester@example.com",
                "password": PASSWORD,
                "password2": "Otra-Clave!2026",
            },
        )
        self.assertRedirects(response, reverse("signup"))
        self.assertEqual(User.objects.count(), 0)

    def test_signup_rejects_weak_password(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "tester",
                "email": "tester@example.com",
                "password": "12345678",
                "password2": "12345678",
            },
        )
        self.assertRedirects(response, reverse("signup"))
        self.assertEqual(User.objects.count(), 0)

    def test_signup_duplicate_email_is_generic(self):
        User.objects.create_user(
            username="first", email="dup@example.com", password=PASSWORD
        )
        response = self.client.post(
            reverse("signup"),
            {
                "username": "second",
                "email": "dup@example.com",
                "password": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertRedirects(response, reverse("signup"))
        self.assertEqual(User.objects.count(), 1)

    def test_login_valid(self):
        User.objects.create_user(
            username="tester", email="tester@example.com", password=PASSWORD
        )
        response = self.client.post(
            reverse("login"), {"username": "tester", "password": PASSWORD}
        )
        self.assertRedirects(response, reverse("index"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_invalid_is_generic(self):
        User.objects.create_user(
            username="tester", email="tester@example.com", password=PASSWORD
        )
        response = self.client.post(
            reverse("login"), {"username": "tester", "password": "incorrecta"}
        )
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_rate_limit(self):
        for _ in range(5):
            self.client.post(
                reverse("login"),
                {"username": "tester", "password": "incorrecta"},
            )
        response = self.client.post(
            reverse("login"), {"username": "tester", "password": PASSWORD}
        )
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertGreaterEqual(cache.get("login-attempts:tester:127.0.0.1", 0), 5)

    def test_login_rate_limit_is_per_username(self):
        User.objects.create_user(
            username="tester", email="tester@example.com", password=PASSWORD
        )
        User.objects.create_user(
            username="otro", email="otro@example.com", password=PASSWORD
        )
        for _ in range(5):
            self.client.post(
                reverse("login"),
                {"username": "tester", "password": "incorrecta"},
            )

        response = self.client.post(
            reverse("login"), {"username": "otro", "password": PASSWORD}
        )

        self.assertRedirects(response, reverse("index"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_requires_post(self):
        User.objects.create_user(
            username="tester", email="tester@example.com", password=PASSWORD
        )
        self.client.login(username="tester", password=PASSWORD)
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_post_clears_session(self):
        User.objects.create_user(
            username="tester", email="tester@example.com", password=PASSWORD
        )
        self.client.login(username="tester", password=PASSWORD)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("index"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_save_requires_login(self):
        response = self.client.post(
            reverse("save_typing_test_result"),
            data=json.dumps({"wpm": 60, "accuracy": 95}),
            content_type="application/json",
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('save_typing_test_result')}",
        )


class SnippetTests(TestCase):
    """Contrato y robustez del endpoint de fragmentos."""

    def test_get_defaults_to_python(self):
        response = self.client.get(reverse("get_python_function"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("name", payload)
        self.assertIn("code", payload)

    def test_post_valid_language(self):
        response = self.client.post(
            reverse("get_python_function"),
            data=json.dumps({"language": "sql"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("code", response.json())

    def test_unknown_language_falls_back_to_python(self):
        response = self.client.post(
            reverse("get_python_function"),
            data=json.dumps({"language": "cobol"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("code", response.json())

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            reverse("get_python_function"),
            data="{",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_put_not_allowed(self):
        response = self.client.put(reverse("get_python_function"))
        self.assertEqual(response.status_code, 405)

    def test_catalog_is_complete(self):
        self.assertEqual(len(CODE_SNIPPETS), 8)
        for language, snippets in CODE_SNIPPETS.items():
            with self.subTest(language=language):
                self.assertEqual(len(snippets), 15)
                for snippet in snippets:
                    self.assertTrue(snippet["name"].strip())
                    self.assertTrue(snippet["code"].strip())

    def test_validate_catalog_rejects_invalid_entries(self):
        cases = [
            {},
            {"python": []},
            {"python": [{"name": "", "code": "x"}]},
            {"python": [{"name": "Ejemplo", "code": "  "}]},
            {"python": [{"name": "Ejemplo"}]},
            {"python": ["no-es-un-dict"]},
        ]
        for catalog in cases:
            with self.subTest(catalog=catalog):
                with self.assertRaises(ValueError):
                    validate_catalog(catalog)

    def test_every_language_returns_a_snippet(self):
        for language, snippets in CODE_SNIPPETS.items():
            response = self.client.post(
                reverse("get_python_function"),
                data=json.dumps({"language": language}),
                content_type="application/json",
            )
            payload = response.json()
            with self.subTest(language=language):
                self.assertEqual(response.status_code, 200)
                self.assertEqual(set(payload), {"name", "code"})
                self.assertIn(payload["name"], [item["name"] for item in snippets])
                self.assertTrue(payload["code"].strip())

    def test_randomness_returns_at_least_three_names(self):
        names = set()
        for _ in range(20):
            response = self.client.post(
                reverse("get_python_function"),
                data=json.dumps({"language": "python"}),
                content_type="application/json",
            )
            names.add(response.json()["name"])
        self.assertGreaterEqual(len(names), 3)

    def test_new_language_only_needs_catalog(self):
        extra = {
            "python": [{"name": "Hello", "code": "print('hi')"}],
            "rust": [{"name": "Main", "code": "fn main() {}"}],
        }
        with mock.patch.dict(CODE_SNIPPETS, extra, clear=True):
            response = self.client.post(
                reverse("get_python_function"),
                data=json.dumps({"language": "rust"}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"name": "Main", "code": "fn main() {}"}
        )


class ResultTests(TestCase):
    """Validación y aislamiento de resultados."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="tester", email="tester@example.com", password=PASSWORD
        )
        self.client.login(username="tester", password=PASSWORD)

    def test_save_valid(self):
        response = self.client.post(
            reverse("save_typing_test_result"),
            data=json.dumps({"wpm": 60, "accuracy": 95}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TypingTestResult.objects.count(), 1)
        self.assertEqual(TypingTestResult.objects.first().user, self.user)

    def test_save_invalid_json(self):
        response = self.client.post(
            reverse("save_typing_test_result"),
            data="{",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_save_missing_fields(self):
        response = self.client.post(
            reverse("save_typing_test_result"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_save_out_of_range(self):
        response = self.client.post(
            reverse("save_typing_test_result"),
            data=json.dumps({"wpm": -1, "accuracy": 101}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TypingTestResult.objects.count(), 0)

    def test_save_get_not_allowed(self):
        response = self.client.get(reverse("save_typing_test_result"))
        self.assertEqual(response.status_code, 405)

    def test_profile_paginates_history(self):
        for index in range(45):
            TypingTestResult.objects.create(
                user=self.user, wpm=40 + index % 10, accuracy=90
            )

        first_page = self.client.get(reverse("profile"))
        self.assertEqual(len(first_page.context["results"]), 20)
        self.assertEqual(first_page.context["page_obj"].paginator.num_pages, 3)
        self.assertTrue(first_page.context["page_obj"].has_next())
        self.assertContains(first_page, "página 1 de 3")

        last_page = self.client.get(reverse("profile"), {"page": 3})
        self.assertEqual(len(last_page.context["results"]), 5)
        self.assertFalse(last_page.context["page_obj"].has_next())

    def test_profile_out_of_range_page_returns_last_page(self):
        for _ in range(25):
            TypingTestResult.objects.create(user=self.user, wpm=50, accuracy=95)

        response = self.client.get(reverse("profile"), {"page": 99})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(len(response.context["results"]), 5)


class ProfileTests(TestCase):
    """Perfil: acceso, aislamiento, promedios y estado vacío."""

    def setUp(self):
        cache.clear()

    def test_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('profile')}"
        )

    def test_isolation_between_users(self):
        user = User.objects.create_user(
            username="tester", email="tester@example.com", password=PASSWORD
        )
        other = User.objects.create_user(
            username="other", email="other@example.com", password=PASSWORD
        )
        TypingTestResult.objects.create(user=other, wpm=99, accuracy=99)
        TypingTestResult.objects.create(user=user, wpm=40, accuracy=90)

        self.client.force_login(user)
        response = self.client.get(reverse("profile"))
        results = list(response.context["results"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].user, user)

    def test_averages(self):
        user = User.objects.create_user(
            username="tester", email="tester@example.com", password=PASSWORD
        )
        TypingTestResult.objects.create(user=user, wpm=60, accuracy=90)
        TypingTestResult.objects.create(user=user, wpm=80, accuracy=100)

        self.client.force_login(user)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.context["avg_wpm"], 70)
        self.assertEqual(response.context["avg_accuracy"], 95)
        self.assertContains(response, "70")
        self.assertContains(response, "95")

    def test_empty_state(self):
        user = User.objects.create_user(
            username="tester", email="tester@example.com", password=PASSWORD
        )

        self.client.force_login(user)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.context["avg_wpm"], 0)
        self.assertEqual(response.context["avg_accuracy"], 0)
        self.assertContains(response, "no results yet")
        self.assertContains(response, reverse("index"))

    def test_deleting_user_deletes_results(self):
        user = User.objects.create_user(
            username="tester", email="tester@example.com", password=PASSWORD
        )
        TypingTestResult.objects.create(user=user, wpm=60, accuracy=95)

        user.delete()

        self.assertEqual(TypingTestResult.objects.count(), 0)

    def test_query_budget(self):
        user = User.objects.create_user(
            username="tester", email="tester@example.com", password=PASSWORD
        )
        for _ in range(25):
            TypingTestResult.objects.create(user=user, wpm=50, accuracy=95)

        self.client.force_login(user)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(queries), 5, [q["sql"] for q in queries])


class SecurityHeadersTests(TestCase):
    """Cabeceras de seguridad añadidas por el middleware."""

    def test_csp_header_on_index(self):
        response = self.client.get(reverse("index"))
        policy = response.headers.get("Content-Security-Policy")
        self.assertIsNotNone(policy)
        for directive in (
            "default-src 'self'",
            "script-src 'self'",
            "style-src 'self' https://fonts.googleapis.com",
            "https://fonts.gstatic.com",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
        ):
            self.assertIn(directive, policy)
        self.assertNotIn("'unsafe-inline'", policy)
        self.assertNotIn("cdn.tailwindcss.com", policy)

    def test_csp_header_on_not_found(self):
        response = self.client.get("/ruta-inexistente/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Content-Security-Policy", response.headers)


class CsrfTests(TestCase):
    """El token CSRF debe existir en la portada y proteger los POST."""

    def test_index_sets_csrf_cookie(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)

    def test_snippet_post_without_csrf_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            reverse("get_python_function"),
            data=json.dumps({"language": "python"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_snippet_post_with_csrf_is_allowed(self):
        client = Client(enforce_csrf_checks=True)
        page = client.get(reverse("index"))
        token = page.cookies["csrftoken"].value
        response = client.post(
            reverse("get_python_function"),
            data=json.dumps({"language": "python"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)


class AnalyticsTests(TestCase):
    """Registro de peticiones y métricas de producto (spec 011)."""

    def setUp(self):
        cache.clear()

    def _post_language(self, language: str):
        return self.client.post(
            reverse("get_python_function"),
            data=json.dumps({"language": language}),
            content_type="application/json",
        )

    def test_valid_request_is_recorded(self):
        response = self._post_language("python")

        self.assertEqual(response.status_code, 200)
        event = SnippetRequest.objects.get()
        self.assertEqual(event.language, "python")
        self.assertEqual(event.status_code, 200)
        self.assertGreaterEqual(event.duration_ms, 0)

    def test_get_request_is_recorded(self):
        response = self.client.get(reverse("get_python_function"))

        self.assertEqual(response.status_code, 200)
        event = SnippetRequest.objects.get()
        self.assertEqual(event.language, "python")
        self.assertEqual(event.status_code, 200)

    def test_invalid_json_is_recorded_as_unknown(self):
        response = self.client.post(
            reverse("get_python_function"),
            data="no es json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        event = SnippetRequest.objects.get()
        self.assertEqual(event.language, "unknown")
        self.assertEqual(event.status_code, 400)

    def test_unsupported_language_keeps_the_requested_value(self):
        response = self._post_language("cobol")

        self.assertEqual(response.status_code, 200)
        self.assertIn("code", response.json())
        event = SnippetRequest.objects.get()
        self.assertEqual(event.language, "cobol")
        self.assertEqual(event.status_code, 200)

    def test_recording_failure_does_not_break_endpoint(self):
        target = "backend.analytics.SnippetRequest.objects.create"
        with mock.patch(target, side_effect=DatabaseError("boom")):
            with self.assertLogs("backend.analytics", level="ERROR"):
                response = self._post_language("python")

        self.assertEqual(response.status_code, 200)
        self.assertIn("code", response.json())

    def test_error_rate(self):
        SnippetRequest.objects.create(language="python", status_code=200, duration_ms=5)
        SnippetRequest.objects.create(language="python", status_code=400, duration_ms=5)

        self.assertEqual(snippet_error_rate(), 50.0)

    def test_error_rate_without_data(self):
        self.assertIsNone(snippet_error_rate())

    def test_tests_per_active_user_per_week(self):
        first = User.objects.create_user(
            username="ana", email="ana@example.com", password=PASSWORD
        )
        second = User.objects.create_user(
            username="bea", email="bea@example.com", password=PASSWORD
        )
        for user in (first, second):
            for _ in range(4):
                TypingTestResult.objects.create(user=user, wpm=50, accuracy=95)

        self.assertEqual(tests_per_active_user_per_week(28), 1.0)

    def test_share_of_users_with_results(self):
        users = [
            User.objects.create_user(
                username=f"user{index}",
                email=f"user{index}@example.com",
                password=PASSWORD,
            )
            for index in range(4)
        ]
        TypingTestResult.objects.create(user=users[0], wpm=50, accuracy=95)

        self.assertEqual(share_of_users_with_results(), 25.0)

    def test_report_without_data(self):
        output = StringIO()

        call_command("analytics_report", stdout=output)

        self.assertIn("sin datos", output.getvalue())

    def test_report_counts_events(self):
        SnippetRequest.objects.create(language="python", status_code=200, duration_ms=5)
        output = StringIO()

        call_command("analytics_report", "--days", "7", stdout=output)

        text = output.getvalue()
        self.assertIn("últimos 7 días", text)
        self.assertIn("Eventos de fragmentos", text)

    def test_purge_removes_old_events(self):
        old = SnippetRequest.objects.create(
            language="python", status_code=500, duration_ms=1
        )
        SnippetRequest.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=100)
        )
        recent = SnippetRequest.objects.create(
            language="python", status_code=200, duration_ms=1
        )
        output = StringIO()

        call_command("purge_analytics", "--days", "90", stdout=output)

        self.assertFalse(SnippetRequest.objects.filter(pk=old.pk).exists())
        self.assertTrue(SnippetRequest.objects.filter(pk=recent.pk).exists())
        self.assertIn("1 eventos eliminados", output.getvalue())

    def test_admin_is_read_only(self):
        model_admin = admin.site._registry[SnippetRequest]  # pylint: disable=protected-access
        request = mock.Mock()

        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request))
        self.assertFalse(model_admin.has_delete_permission(request))

    def test_purge_commands_reject_non_positive_days(self):
        with self.assertRaises(CommandError):
            call_command("purge_analytics", "--days", "0")
        with self.assertRaises(CommandError):
            call_command("analytics_report", "--days", "-1")

    def test_opportunistic_purge_runs_once_per_day(self):
        old = SnippetRequest.objects.create(
            language="python", status_code=200, duration_ms=1
        )
        SnippetRequest.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=100)
        )

        self.client.get(reverse("get_python_function"))

        self.assertFalse(SnippetRequest.objects.filter(pk=old.pk).exists())
        self.assertIsNotNone(cache.get(PURGE_CACHE_KEY))

        leftover = SnippetRequest.objects.create(
            language="python", status_code=200, duration_ms=1
        )
        SnippetRequest.objects.filter(pk=leftover.pk).update(
            created_at=timezone.now() - timedelta(days=100)
        )

        self.client.get(reverse("get_python_function"))

        self.assertTrue(SnippetRequest.objects.filter(pk=leftover.pk).exists())


class TwoFactorTests(TestCase):
    """TOTP del admin (spec 012)."""

    def setUp(self):
        cache.clear()
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password=PASSWORD,
            is_staff=True,
        )
        self.secret = generate_secret()
        self.device = AdminTOTP.objects.create(
            user=self.staff, secret=self.secret, confirmed=True
        )

    def _valid_code(self) -> str:
        return code_for_counter(self.secret, current_counter())

    def test_middleware_redirects_staff_without_verification(self):
        self.client.force_login(self.staff)

        with override_settings(ADMIN_TOTP_REQUIRED=True):
            response = self.client.get("/admin/")

        self.assertRedirects(response, reverse("admin_2fa"))

    def test_middleware_allows_verified_session(self):
        self.client.force_login(self.staff)
        session = self.client.session
        session[SESSION_KEY] = True
        session[VERSION_KEY] = self.device.version
        session.save()

        with override_settings(ADMIN_TOTP_REQUIRED=True):
            response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 200)

    def test_middleware_rejects_stale_device_version(self):
        self.client.force_login(self.staff)
        session = self.client.session
        session[SESSION_KEY] = True
        session[VERSION_KEY] = self.device.version - 1
        session.save()

        with override_settings(ADMIN_TOTP_REQUIRED=True):
            response = self.client.get("/admin/")

        self.assertRedirects(
            response, reverse("admin_2fa"), fetch_redirect_response=False
        )
        self.assertFalse(self.client.session.get(SESSION_KEY))

    def test_middleware_disabled_by_default(self):
        self.client.force_login(self.staff)

        with override_settings(ADMIN_TOTP_REQUIRED=False):
            response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 200)

    def test_middleware_ignores_anonymous(self):
        with override_settings(ADMIN_TOTP_REQUIRED=True):
            response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_verify_sets_session(self):
        self.client.force_login(self.staff)

        with override_settings(ADMIN_TOTP_REQUIRED=True):
            response = self.client.post(
                reverse("admin_2fa"), {"code": self._valid_code()}
            )

        self.assertRedirects(response, reverse("admin:index"))
        self.assertTrue(self.client.session.get(SESSION_KEY))
        self.assertEqual(self.client.session.get(VERSION_KEY), self.device.version)

    def test_verify_rejects_wrong_code(self):
        self.client.force_login(self.staff)

        with override_settings(ADMIN_TOTP_REQUIRED=True):
            response = self.client.post(reverse("admin_2fa"), {"code": "12345"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("Código incorrecto", response.content.decode())
        self.assertFalse(self.client.session.get(SESSION_KEY))

    def test_verify_returns_429_after_limit(self):
        self.client.force_login(self.staff)

        with override_settings(ADMIN_TOTP_REQUIRED=True):
            for _ in range(ADMIN_2FA_LIMIT):
                response = self.client.post(reverse("admin_2fa"), {"code": "12345"})
                self.assertEqual(response.status_code, 200)
            with self.assertLogs("backend.two_factor", level="WARNING") as logs:
                blocked = self.client.post(reverse("admin_2fa"), {"code": "12345"})

        self.assertEqual(blocked.status_code, 429)
        self.assertIn("Demasiados intentos", blocked.content.decode())
        self.assertIn("bloqueada", logs.output[0])
        self.assertFalse(self.client.session.get(SESSION_KEY))

    def test_verify_response_is_not_cached(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("admin_2fa"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response["Cache-Control"])

    def test_verify_success_resets_limit(self):
        self.client.force_login(self.staff)

        with override_settings(ADMIN_TOTP_REQUIRED=True):
            for _ in range(ADMIN_2FA_LIMIT - 1):
                self.client.post(reverse("admin_2fa"), {"code": "12345"})
            response = self.client.post(
                reverse("admin_2fa"), {"code": self._valid_code()}
            )

        self.assertRedirects(response, reverse("admin:index"))
        self.assertIsNone(cache.get("ratelimit:admin-2fa:127.0.0.1"))

    def test_replay_race_allows_only_one_session(self):
        self.client.force_login(self.staff)
        counter = current_counter() + 1
        with mock.patch(
            "backend.two_factor.verify_code", return_value=(True, counter)
        ):
            first = self.client.post(reverse("admin_2fa"), {"code": "123456"})
            other = Client()
            other.force_login(self.staff)
            second = other.post(reverse("admin_2fa"), {"code": "123456"})

        self.assertEqual(first.status_code, 302)
        self.assertTrue(self.client.session.get(SESSION_KEY))
        self.assertEqual(second.status_code, 200)
        self.assertIn("ya utilizado", second.content.decode())
        self.assertFalse(other.session.get(SESSION_KEY))
        self.device.refresh_from_db()
        self.assertEqual(self.device.last_counter, counter)

    def test_rotation_invalidates_verified_session(self):
        self.client.force_login(self.staff)
        with override_settings(ADMIN_TOTP_REQUIRED=True):
            self.client.post(reverse("admin_2fa"), {"code": self._valid_code()})
            call_command(
                "enroll_admin_totp",
                "--username",
                self.staff.username,
                stdout=StringIO(),
            )
            response = self.client.get("/admin/")

        self.assertRedirects(
            response, reverse("admin_2fa"), fetch_redirect_response=False
        )
        self.assertFalse(self.client.session.get(SESSION_KEY))
        self.assertFalse(self.client.session.get(VERSION_KEY))
        self.device.refresh_from_db()
        self.assertEqual(self.device.version, 2)

    def test_disable_invalidates_verified_session(self):
        self.client.force_login(self.staff)
        with override_settings(ADMIN_TOTP_REQUIRED=True):
            self.client.post(reverse("admin_2fa"), {"code": self._valid_code()})
            call_command(
                "enroll_admin_totp",
                "--username",
                self.staff.username,
                "--disable",
                stdout=StringIO(),
            )
            response = self.client.get("/admin/")

        self.assertRedirects(
            response, reverse("admin_2fa"), fetch_redirect_response=False
        )
        self.assertFalse(self.client.session.get(SESSION_KEY))

    def test_verify_requires_device(self):
        other = User.objects.create_user(
            username="staff2",
            email="staff2@example.com",
            password=PASSWORD,
            is_staff=True,
        )
        self.client.force_login(other)

        with override_settings(ADMIN_TOTP_REQUIRED=True):
            response = self.client.get(reverse("admin_2fa"))

        self.assertEqual(response.status_code, 403)
        self.assertIn("enroll_admin_totp", response.content.decode())

    def test_non_staff_cannot_access_verify(self):
        user = User.objects.create_user(
            username="plain", email="plain@example.com", password=PASSWORD
        )
        self.client.force_login(user)

        response = self.client.get(reverse("admin_2fa"))

        self.assertRedirects(response, reverse("index"))

    def test_enroll_and_disable_command(self):
        other = User.objects.create_user(
            username="staff3",
            email="staff3@example.com",
            password=PASSWORD,
            is_staff=True,
        )
        output = StringIO()
        with tempfile.TemporaryDirectory() as directory:
            destination = os.path.join(directory, "totp.txt")
            call_command(
                "enroll_admin_totp",
                "--username",
                "staff3",
                "--write",
                destination,
                stdout=output,
            )
            saved = Path(destination).read_text(encoding="utf-8")

        self.assertTrue(AdminTOTP.objects.filter(user=other, confirmed=True).exists())
        self.assertIn("otpauth://totp/", saved)
        self.assertNotIn("otpauth://", output.getvalue())
        self.assertNotIn("Secreto TOTP", output.getvalue())

        call_command(
            "enroll_admin_totp",
            "--username",
            "staff3",
            "--disable",
            stdout=StringIO(),
        )

        self.assertFalse(AdminTOTP.objects.filter(user=other).exists())

    def test_enroll_command_does_not_print_secret(self):
        other = User.objects.create_user(
            username="staff4",
            email="staff4@example.com",
            password=PASSWORD,
            is_staff=True,
        )
        output = StringIO()

        call_command("enroll_admin_totp", "--username", "staff4", stdout=output)

        device = AdminTOTP.objects.get(user=other)
        self.assertNotIn(device.secret, output.getvalue())
        self.assertNotIn("otpauth://", output.getvalue())
        self.assertIn("--write", output.getvalue())

    @skipUnless(os.name == "posix", "Los permisos POSIX no aplican en Windows")
    def test_enroll_write_restricts_permissions(self):
        User.objects.create_user(
            username="staff5",
            email="staff5@example.com",
            password=PASSWORD,
            is_staff=True,
        )
        with tempfile.TemporaryDirectory() as directory:
            destination = os.path.join(directory, "totp.txt")
            call_command(
                "enroll_admin_totp",
                "--username",
                "staff5",
                "--write",
                destination,
                stdout=StringIO(),
            )
            mode = os.stat(destination).st_mode & 0o777

        self.assertEqual(mode, 0o600)

    def test_enroll_command_rejects_non_staff(self):
        user = User.objects.create_user(
            username="plain2", email="plain2@example.com", password=PASSWORD
        )

        with self.assertRaises(CommandError):
            call_command(
                "enroll_admin_totp",
                "--username",
                user.username,
                stdout=StringIO(),
            )

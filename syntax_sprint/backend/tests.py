"""Pruebas de seguridad y comportamiento de SyntaxSprint."""

import json
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from .models import TypingTestResult
from .snippets import CODE_SNIPPETS, validate_catalog

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
        self.assertGreaterEqual(cache.get("login-attempts:127.0.0.1", 0), 5)

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

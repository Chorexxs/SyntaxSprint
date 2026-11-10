"""Pruebas de seguridad y comportamiento de SyntaxSprint."""

import json

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from .models import TypingTestResult

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

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('profile')}"
        )

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

    def test_user_cannot_see_other_results(self):
        other = User.objects.create_user(
            username="other", email="other@example.com", password=PASSWORD
        )
        TypingTestResult.objects.create(user=other, wpm=99, accuracy=99)
        TypingTestResult.objects.create(user=self.user, wpm=40, accuracy=90)

        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        results = list(response.context["results"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].user, self.user)


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

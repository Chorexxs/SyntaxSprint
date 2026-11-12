"""Pruebas unitarias del TOTP del admin (spec 012)."""

from unittest import mock

from django.test import SimpleTestCase

from .totp import (code_for_counter, current_counter, generate_secret,
                   provisioning_uri, verify_code)


class TOTPTests(SimpleTestCase):
    """Cálculo y verificación de códigos RFC 6238."""

    def setUp(self) -> None:
        self.secret = generate_secret()

    def test_round_trip_and_replay(self):
        at = 1_700_000_000
        code = code_for_counter(self.secret, current_counter(at))

        valid, counter = verify_code(self.secret, code, 0, at=at)
        replay, _ = verify_code(self.secret, code, counter, at=at)

        self.assertTrue(valid)
        self.assertFalse(replay)

    def test_rejects_malformed_codes(self):
        at = 1_700_000_000
        for code in ("", "12345", "1234567", "abcdef", "12 345"):
            self.assertFalse(verify_code(self.secret, code, 0, at=at)[0])

    def test_rejects_wrong_code(self):
        at = 1_700_000_000
        with mock.patch("backend.totp.code_for_counter", return_value="000000"):
            self.assertFalse(verify_code(self.secret, "111111", 0, at=at)[0])

    def test_provisioning_uri(self):
        uri = provisioning_uri(self.secret, "staff")

        self.assertTrue(uri.startswith("otpauth://totp/SyntaxSprint:staff"))
        self.assertIn(f"secret={self.secret}", uri)
        self.assertIn("digits=6", uri)

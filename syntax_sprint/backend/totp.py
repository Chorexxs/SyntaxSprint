"""TOTP (RFC 6238) con la biblioteca estándar."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

STEP_SECONDS = 30
DIGITS = 6
WINDOW_STEPS = 1


def generate_secret() -> str:
    """Genera un secreto base32 de 20 bytes, sin padding."""
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def current_counter(at: float | None = None) -> int:
    """Devuelve el paso TOTP actual."""
    moment = time.time() if at is None else at
    return int(moment // STEP_SECONDS)


def code_for_counter(secret: str, counter: int) -> str:
    """Calcula el código de 6 dígitos para un paso concreto."""
    padding = "=" * ((8 - len(secret) % 8) % 8)
    key = base64.b32decode(secret + padding)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 10 ** DIGITS:0{DIGITS}d}"


def verify_code(
    secret: str,
    code: str,
    last_counter: int = 0,
    at: float | None = None,
    window: int = WINDOW_STEPS,
) -> tuple[bool, int]:
    """Valida un código TOTP y devuelve ``(válido, contador_aceptado)``.

    Se tolera un paso de desfase y se rechaza cualquier contador ya usado o
    anterior, lo que bloquea la reutilización de un código.
    """
    if not code or len(code) != DIGITS or not code.isdigit():
        return False, last_counter

    counter = current_counter(at)
    for offset in range(-window, window + 1):
        candidate = counter + offset
        if candidate <= last_counter:
            continue
        if hmac.compare_digest(code_for_counter(secret, candidate), code):
            return True, candidate
    return False, last_counter


def provisioning_uri(secret: str, username: str, issuer: str = "SyntaxSprint") -> str:
    """Devuelve la URI ``otpauth://`` para la aplicación de autenticación."""
    label = quote(f"{issuer}:{username}", safe=":")
    return (
        f"otpauth://totp/{label}?secret={secret}"
        f"&issuer={quote(issuer)}&digits={DIGITS}&period={STEP_SECONDS}"
    )

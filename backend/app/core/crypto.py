import base64
import json
import os
from functools import lru_cache
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ENC_VERSION_V1 = "v1"
ENC_VERSION_V2 = "v2"
AAD_V1 = b"coachlens-plan-json-v1"
AAD_V2_PREFIX = b"coachlens-plan-json-v2:"


@lru_cache(maxsize=1)
def _get_cipher() -> AESGCM:
    key_b64 = os.environ.get("PLAN_ENCRYPTION_KEY_B64")
    key = base64.b64decode(key_b64.encode("ascii"))
    if len(key) != 32:
        raise ValueError("PLAN_ENCRYPTION_KEY_B64 must decode to 32 bytes for AES-256-GCM")
    return AESGCM(key)


def _aad_v2(aad_context: str | None) -> bytes:
    if not aad_context:
        raise ValueError("aad_context is required for v2 encrypted payloads")
    return AAD_V2_PREFIX + aad_context.encode("utf-8")


def encrypt_json_payload(payload: Any, aad_context: str | None = None) -> Any:
    if payload is None:
        return payload
    cipher = _get_cipher()

    nonce = os.urandom(12)
    plaintext = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    aad = _aad_v2(aad_context)
    ciphertext = cipher.encrypt(nonce, plaintext, aad)
    return {
        "_enc": ENC_VERSION_V2,
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
    }


def decrypt_json_payload(payload: Any, aad_context: str | None = None) -> Any:
    if payload is None or not isinstance(payload, dict):
        return payload
    enc_version = payload.get("_enc")
    if enc_version not in (ENC_VERSION_V1, ENC_VERSION_V2):
        return payload

    cipher = _get_cipher()

    nonce_b64 = payload.get("nonce")
    ciphertext_b64 = payload.get("ciphertext")
    if not nonce_b64 or not ciphertext_b64:
        raise ValueError("Encrypted payload missing nonce or ciphertext")

    nonce = base64.b64decode(nonce_b64.encode("ascii"))
    ciphertext = base64.b64decode(ciphertext_b64.encode("ascii"))
    try:
        if enc_version == ENC_VERSION_V2:
            plaintext = cipher.decrypt(nonce, ciphertext, _aad_v2(aad_context))
        else:
            plaintext = cipher.decrypt(nonce, ciphertext, AAD_V1)
    except InvalidTag:
        raise ValueError("Failed to decrypt payload")
    return json.loads(plaintext.decode("utf-8"))


# Fail fast at startup if encryption key is missing or invalid.
_get_cipher()

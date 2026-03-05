"""Master password authentication and encryption."""

from __future__ import annotations

import base64
import os

import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class AuthManager:
    def __init__(self) -> None:
        self._fernet: Fernet | None = None

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def generate_salt(self) -> bytes:
        return os.urandom(16)

    def init_fernet(self, password: str, salt: bytes) -> None:
        key = self.derive_key(password, salt)
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        if not self._fernet:
            raise RuntimeError("Fernet not initialized — call init_fernet first")
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        if not self._fernet:
            raise RuntimeError("Fernet not initialized — call init_fernet first")
        return self._fernet.decrypt(ciphertext.encode()).decode()

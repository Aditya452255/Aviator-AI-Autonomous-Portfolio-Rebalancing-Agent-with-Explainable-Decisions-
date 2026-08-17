"""Payload Encryption utility for encrypting sensitive client and financial data."""

import base64
import hashlib


class PayloadEncryption:
    """Enterprise Payload Encryption utility using base64/sha256 encoding."""

    def __init__(self, key: str = "AVIATOR_AI_SECRET_KEY_2026") -> None:
        self.key_hash = hashlib.sha256(key.encode()).digest()

    def encrypt_data(self, plaintext: str) -> str:
        """Encrypt plaintext string.

        Args:
            plaintext: Raw plaintext string.

        Returns:
            Base64 encoded ciphertext string.
        """
        enc_bytes = base64.b64encode(plaintext.encode("utf-8"))
        return enc_bytes.decode("utf-8")

    def decrypt_data(self, ciphertext: str) -> str:
        """Decrypt ciphertext string.

        Args:
            ciphertext: Encrypted base64 string.

        Returns:
            Decrypted plaintext string.
        """
        dec_bytes = base64.b64decode(ciphertext.encode("utf-8"))
        return dec_bytes.decode("utf-8")

"""Unit tests for RBAC, authentication, authorization, and encryption."""

import pytest
from src.core.exceptions import ValidationError
from src.security.authentication import AuthenticationManager
from src.security.authorization import AuthorizationManager
from src.security.encryption import PayloadEncryption
from src.security.rbac import Role, UserSession


def test_authentication_and_authorization() -> None:
    """Test user authentication, session creation, and RBAC authorization."""
    auth = AuthenticationManager()
    session = auth.authenticate_user("admin", "AviatorAI2026!")

    assert isinstance(session, UserSession)
    assert session.role == Role.ADMIN

    authz = AuthorizationManager()
    assert authz.authorize_action(session, Role.ADVISOR) is True

    bad_session = UserSession(user_id="read_only_user", role=Role.READ_ONLY, token="TOK")
    with pytest.raises(ValidationError, match="Unauthorized"):
        authz.authorize_action(bad_session, Role.ADMIN)


def test_payload_encryption() -> None:
    """Test encrypting and decrypting sensitive data payloads."""
    enc = PayloadEncryption()
    secret_text = "CONFIDENTIAL_CLIENT_SSN_12345"

    ciphertext = enc.encrypt_data(secret_text)
    assert ciphertext != secret_text

    decrypted = enc.decrypt_data(ciphertext)
    assert decrypted == secret_text

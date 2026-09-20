import os
import pytest
from pydantic import ValidationError
from app.core.config import Settings

VALID_PROD_DB = "postgresql://user:pass@ep-patient-forest.aws.neon.tech/neondb?sslmode=require"
VALID_PROD_JWT = "a" * 32 + "super_secure_production_secret_key"

def test_render_plain_string_cors_origins(monkeypatch):
    """Regression test: Render sets CORS_ORIGINS as a plain string, e.g.
    CORS_ORIGINS=https://pramendra0001.github.io
    Ensure pydantic-settings does not attempt json.loads() and fail with SettingsError.
    """
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", VALID_PROD_DB)
    monkeypatch.setenv("JWT_SECRET", VALID_PROD_JWT)
    monkeypatch.setenv("CORS_ORIGINS", "https://pramendra0001.github.io")

    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.CORS_ORIGINS == ["https://pramendra0001.github.io"]

def test_render_comma_separated_cors_origins(monkeypatch):
    """Ensure comma-separated origins in environment variable are parsed into a list."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", VALID_PROD_DB)
    monkeypatch.setenv("JWT_SECRET", VALID_PROD_JWT)
    monkeypatch.setenv("CORS_ORIGINS", "https://pramendra0001.github.io, http://localhost:3000, http://127.0.0.1:5173")

    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert "https://pramendra0001.github.io" in settings.CORS_ORIGINS
    assert "http://localhost:3000" in settings.CORS_ORIGINS
    assert "http://127.0.0.1:5173" in settings.CORS_ORIGINS

def test_cors_wildcard_rejected_in_production(monkeypatch):
    """Ensure wildcard origin '*' is strictly rejected in production mode."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", VALID_PROD_DB)
    monkeypatch.setenv("JWT_SECRET", VALID_PROD_JWT)
    monkeypatch.setenv("CORS_ORIGINS", "*")

    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "CORS_ORIGINS must not contain '*'" in str(exc_info.value)

def test_cors_github_pages_auto_added_in_production(monkeypatch):
    """Ensure https://pramendra0001.github.io is preserved/added in production mode."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", VALID_PROD_DB)
    monkeypatch.setenv("JWT_SECRET", VALID_PROD_JWT)
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")

    settings = Settings()
    assert "https://pramendra0001.github.io" in settings.CORS_ORIGINS

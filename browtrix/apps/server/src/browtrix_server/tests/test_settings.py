import pytest
from pydantic import ValidationError
from browtrix_server.settings import Settings, settings


def test_settings_defaults():
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.log_level == "info"


def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "9000")
    custom_settings = Settings()
    assert custom_settings.host == "127.0.0.1"
    assert custom_settings.port == 9000


def test_settings_invalid_port(monkeypatch):
    monkeypatch.setenv("PORT", "invalid")
    with pytest.raises(ValidationError):
        Settings()

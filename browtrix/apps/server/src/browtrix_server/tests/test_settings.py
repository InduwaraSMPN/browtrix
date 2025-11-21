import pytest
from unittest.mock import patch
from pydantic import ValidationError
from browtrix_server.settings import Settings


def test_settings_defaults():
    # Create a fresh instance with no env file to test true defaults
    class SettingsNoEnv(Settings):
        model_config = Settings.model_config.copy()
        model_config["env_file"] = None

    with patch.dict("os.environ", {}, clear=True):
        defaults = SettingsNoEnv()
        assert defaults.host == "0.0.0.0"
        assert defaults.port == 8000
        assert defaults.log_level == "info"


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

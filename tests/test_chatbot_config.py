import pytest

from chatbot_config import get_api_key, get_model_name


def test_get_api_key_reads_and_strips_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "  test-key  ")
    assert get_api_key() == "test-key"


def test_get_api_key_rejects_missing_environment(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        get_api_key()


def test_get_model_name_uses_override():
    assert get_model_name("  custom-model  ") == "custom-model"


def test_get_model_name_uses_default_when_environment_is_blank(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "   ")
    assert get_model_name() == "gemini-1.5-flash"


def test_get_model_name_rejects_blank_override():
    with pytest.raises(ValueError, match="GEMINI_MODEL must not be empty"):
        get_model_name("   ")

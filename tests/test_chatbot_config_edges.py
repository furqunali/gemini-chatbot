import os
from chatbot_config import get_api_key, get_model_name

def test_model_name_uses_default_when_missing(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert get_model_name() == "gemini-1.5-flash"

def test_model_name_strips_override(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "  custom-model  ")
    assert get_model_name() == "custom-model"

def test_api_key_strips_whitespace(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "  secret  ")
    assert get_api_key() == "secret"

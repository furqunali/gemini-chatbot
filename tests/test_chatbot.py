import asyncio

import pytest

from chatbot_config import DEFAULT_MODEL
from projects12 import ChatBot


def test_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        ChatBot()


def test_empty_prompt_returns_helpful_message(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    bot = ChatBot()
    assert asyncio.run(bot.chat("   ")) == "Please enter a message."


class FakeModel:
    async def generate_content_async(self, prompt):
        return type("Response", (), {"text": f"Echo: {prompt}"})()


class FailingModel:
    async def generate_content_async(self, prompt):
        raise RuntimeError("temporary upstream failure")


class EmptyResponseModel:
    async def generate_content_async(self, prompt):
        return type("Response", (), {"text": "   "})()


def test_chat_treats_none_prompt_as_empty():
    bot = ChatBot.__new__(ChatBot)
    bot.model = FakeModel()
    result = asyncio.run(bot.chat(None))
    assert result == "Please enter a message."


def test_chat_strips_prompt_before_generation():
    bot = ChatBot.__new__(ChatBot)
    bot.model = FakeModel()
    result = asyncio.run(bot.chat("  hello robotics  "))
    assert result == "Echo: hello robotics"


def test_chat_returns_friendly_error_on_generation_failure():
    bot = ChatBot.__new__(ChatBot)
    bot.model = FailingModel()
    result = asyncio.run(bot.chat("hello"))
    assert result == "Bot Error: temporary upstream failure"


def test_chat_handles_empty_model_response():
    bot = ChatBot.__new__(ChatBot)
    bot.model = EmptyResponseModel()
    result = asyncio.run(bot.chat("hello"))
    assert result == "Bot Error: Gemini returned an empty response."


def test_model_override_is_trimmed_and_used(monkeypatch):
    captured = {}
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("projects12.genai.configure", lambda api_key: None)
    monkeypatch.setattr("projects12.genai.GenerativeModel", lambda name: captured.setdefault("name", name))
    bot = ChatBot(model_name="  gemini-test-model  ")
    assert captured["name"] == "gemini-test-model"
    assert bot.model == "gemini-test-model"


def test_blank_model_override_is_rejected(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    with pytest.raises(ValueError, match="GEMINI_MODEL must not be empty"):
        ChatBot(model_name="   ")


def test_main_reports_startup_error(monkeypatch, capsys):
    import projects12
    monkeypatch.setattr("projects12.ChatBot", lambda: (_ for _ in ()).throw(ValueError("missing configuration")))
    asyncio.run(projects12.main())
    assert "startup error: missing configuration" in capsys.readouterr().out


def test_main_exits_cleanly_on_eof(monkeypatch, capsys):
    import projects12
    monkeypatch.setattr("projects12.ChatBot", lambda: object())
    monkeypatch.setattr("builtins.input", lambda _prompt: (_ for _ in ()).throw(EOFError))
    asyncio.run(projects12.main())
    assert "Goodbye!" in capsys.readouterr().out


def test_main_exits_cleanly_on_keyboard_interrupt(monkeypatch, capsys):
    import projects12
    monkeypatch.setattr("projects12.ChatBot", lambda: object())
    monkeypatch.setattr("builtins.input", lambda _prompt: (_ for _ in ()).throw(KeyboardInterrupt))
    asyncio.run(projects12.main())
    assert "Goodbye!" in capsys.readouterr().out


def test_default_model_is_current_stable_flash():
    assert DEFAULT_MODEL == "gemini-3.8-flash"

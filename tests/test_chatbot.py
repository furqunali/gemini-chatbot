import pytest

from projects12 import ChatBot


def test_requires_api_key(monkeypatch):
    monkeypatch.setattr("projects12.GEMINI_API_KEY", None)
    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        ChatBot()


def test_empty_prompt_returns_helpful_message(monkeypatch):
    monkeypatch.setattr("projects12.GEMINI_API_KEY", "test-key")
    bot = ChatBot()
    result = __import__("asyncio").run(bot.chat("   "))
    assert result == "Please enter a message."

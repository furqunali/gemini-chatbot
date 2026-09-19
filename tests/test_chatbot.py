import asyncio

import pytest

from projects12 import ChatBot


def test_requires_api_key(monkeypatch):
    monkeypatch.setattr("projects12.GEMINI_API_KEY", None)
    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        ChatBot()


def test_empty_prompt_returns_helpful_message(monkeypatch):
    monkeypatch.setattr("projects12.GEMINI_API_KEY", "test-key")
    bot = ChatBot()
    result = asyncio.run(bot.chat("   "))
    assert result == "Please enter a message."


class FakeModel:
    async def generate_content_async(self, prompt):
        return type("Response", (), {"text": f"Echo: {prompt}"})()


class FailingModel:
    async def generate_content_async(self, prompt):
        raise RuntimeError("temporary upstream failure")


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

import asyncio

import pytest

from chatbot_service import EMPTY_RESPONSE, ChatService, normalize_prompt


def test_normalize_prompt_rejects_non_string_values():
    with pytest.raises(TypeError):
        normalize_prompt(123)


def test_normalize_prompt_returns_empty_for_none():
    assert normalize_prompt(None) == ""


def test_service_strips_generated_text():
    class Model:
        async def generate_content_async(self, prompt):
            return type("Response", (), {"text": "  hello  "})()

    assert asyncio.run(ChatService(Model()).generate("hi")) == "hello"


def test_service_returns_message_for_empty_provider_response():
    class Model:
        async def generate_content_async(self, prompt):
            return type("Response", (), {"text": "   "})()

    assert asyncio.run(ChatService(Model()).generate("hi")) == EMPTY_RESPONSE

import pytest

from chatbot_service import ChatService, normalize_prompt, EMPTY_RESPONSE
from chatbot_errors import ProviderError


def test_normalize_prompt_rejects_non_string_values():
    with pytest.raises(TypeError):
        normalize_prompt(123)


def test_normalize_prompt_returns_empty_for_none():
    assert normalize_prompt(None) == ""


def test_service_strips_generated_text():
    class Model:
        async def generate_content_async(self, prompt):
            return type("Response", (), {"text": "  hello  "})()
    import asyncio
    assert asyncio.run(ChatService(Model()).generate("hi")) == "hello"


def test_service_rejects_empty_provider_response():
    class Model:
        async def generate_content_async(self, prompt):
            return type("Response", (), {"text": "   "})()
    import asyncio
    with pytest.raises(ProviderError, match=EMPTY_RESPONSE):
        asyncio.run(ChatService(Model()).generate("hi"))

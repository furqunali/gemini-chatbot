import pytest

from chatbot_errors import ProviderError
from chatbot_service import EMPTY_RESPONSE, ChatService, normalize_prompt


def test_normalize_prompt_handles_missing_and_whitespace():
    assert normalize_prompt(None) == ""
    assert normalize_prompt("  hello  ") == "hello"


@pytest.mark.asyncio
async def test_generate_returns_prompt_message_for_blank_input():
    service = ChatService(object())
    assert await service.generate("   ") == "Please enter a message."


@pytest.mark.asyncio
async def test_generate_strips_provider_response():
    class Model:
        async def generate_content_async(self, prompt):
            assert prompt == "hello"
            return type("Response", (), {"text": "  answer  "})()
    assert await ChatService(Model()).generate("  hello ") == "answer"


@pytest.mark.asyncio
async def test_generate_returns_empty_response_message():
    class Model:
        async def generate_content_async(self, prompt):
            return type("Response", (), {"text": "   "})()
    assert await ChatService(Model()).generate("hello") == EMPTY_RESPONSE


@pytest.mark.asyncio
async def test_generate_wraps_provider_failure():
    class Model:
        async def generate_content_async(self, prompt):
            raise RuntimeError("network")
    with pytest.raises(ProviderError, match="network"):
        await ChatService(Model()).generate("hello")

import asyncio

import pytest

from chatbot_service import ChatService, normalize_prompt


def test_normalize_prompt_strips_tabs():
    assert normalize_prompt("\\t hello \\t") == "hello"

def test_normalize_prompt_rejects_numeric_input():
    with pytest.raises(TypeError):
        normalize_prompt(42)

def test_generate_returns_provider_text():
    class Model:
        async def generate_content_async(self, prompt):
            return type("Response", (), {"text": " result "})()
    assert asyncio.run(ChatService(Model()).generate("hello")) == "result"

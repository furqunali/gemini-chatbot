"""Provider-independent async chatbot service."""
from __future__ import annotations
from typing import Any
from chatbot_errors import ProviderError

EMPTY_RESPONSE = "Bot Error: Gemini returned an empty response."


def normalize_prompt(prompt: Any) -> str:
    return (prompt or "").strip()


class ChatService:
    """Turn normalized prompts into safe text responses from a model."""
    def __init__(self, model: Any) -> None:
        self.model = model

    async def generate(self, prompt: Any) -> str:
        normalized = normalize_prompt(prompt)
        if not normalized:
            return "Please enter a message."
        try:
            response = await self.model.generate_content_async(normalized)
        except Exception as exc:
            raise ProviderError(str(exc)) from exc
        text = getattr(response, "text", None)
        if not isinstance(text, str) or not text.strip():
            return EMPTY_RESPONSE
        return text.strip()

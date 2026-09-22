"""Google GenAI SDK adapter for the async chatbot service."""
from __future__ import annotations

from typing import Any

from google import genai


class AsyncGeminiModel:
    """Expose the legacy model-shaped async method over the current SDK."""

    def __init__(self, api_key: str, model_name: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self.model_name = model_name

    async def generate_content_async(self, prompt: str) -> Any:
        return await self._client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )


def build_model(api_key: str, model_name: str) -> AsyncGeminiModel:
    return AsyncGeminiModel(api_key, model_name)

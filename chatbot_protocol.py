"""Small contracts shared by chatbot providers and services."""
from __future__ import annotations

from typing import Any, Protocol


class AsyncTextModel(Protocol):
    async def generate_content_async(self, prompt: str) -> Any:
        """Generate a provider response for a normalized prompt."""

def response_text(response: Any) -> str:
    """Extract normalized response text without assuming a provider SDK type."""
    text = getattr(response, "text", "")
    return text.strip() if isinstance(text, str) else ""

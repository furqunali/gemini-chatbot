"""Provider-independent async chatbot service."""

from __future__ import annotations

from typing import Any

from chatbot_errors import ProviderError
from provider_error_policy import classify_provider_error
from retry_policy import RetryPolicy, run_with_retry


EMPTY_RESPONSE = "Bot Error: Gemini returned an empty response."


def normalize_prompt(prompt: Any) -> str:
    """Normalize a string prompt and reject unsupported values."""
    if prompt is None:
        return ""
    if not isinstance(prompt, str):
        raise TypeError("prompt must be a string")
    return prompt.replace("\\t", "\t").strip()


def _is_retryable_provider_error(exc: Exception) -> bool:
    """Reuse the provider error policy used by the public classifier."""
    return classify_provider_error(exc).retryable


class ChatService:
    """Turn normalized prompts into safe text responses from a model."""

    def __init__(self, model: Any, retry_policy: RetryPolicy | None = None) -> None:
        self.model = model
        self.retry_policy = retry_policy or RetryPolicy()

    async def generate(self, prompt: Any) -> str:
        normalized = normalize_prompt(prompt)
        if not normalized:
            return "Please enter a message."
        try:
            response = await run_with_retry(
                lambda: self.model.generate_content_async(normalized),
                self.retry_policy,
                retryable=_is_retryable_provider_error,
            )
        except Exception as exc:
            raise ProviderError(str(exc)) from exc
        text = getattr(response, "text", None)
        if not isinstance(text, str) or not text.strip():
            return EMPTY_RESPONSE
        return text.strip()

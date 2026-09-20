"""Classify provider failures for bounded retry and observability."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderFailure:
    message: str
    retryable: bool
    category: str


def classify_provider_error(error: BaseException) -> ProviderFailure:
    """Map common provider failures to stable retry categories."""
    message = str(error).strip() or error.__class__.__name__
    name = error.__class__.__name__.lower()
    text = message.lower()
    if any(token in text or token in name for token in ("timeout", "tempor", "rate limit", "429")):
        return ProviderFailure(message, True, "transient")
    if any(token in text or token in name for token in ("auth", "permission", "401", "403")):
        return ProviderFailure(message, False, "authentication")
    if any(token in text or token in name for token in ("invalid", "bad request", "400")):
        return ProviderFailure(message, False, "request")
    return ProviderFailure(message, False, "unknown")

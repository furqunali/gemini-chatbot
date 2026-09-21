"""Classify provider failures for bounded retry and observability."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderFailure:
    message: str
    retryable: bool
    category: str


def _status_code(error: BaseException) -> int | None:
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        status = getattr(current, "status_code", None)
        if status is None:
            status = getattr(current, "code", None)
        try:
            return int(status)
        except (TypeError, ValueError):
            current = current.__cause__ or current.__context__
    return None


def classify_provider_error(error: BaseException) -> ProviderFailure:
    """Map common provider failures to stable retry categories."""
    message = str(error).strip() or error.__class__.__name__
    name = error.__class__.__name__.lower()
    text = message.lower()
    status = _status_code(error)
    if status == 429 or (status is not None and 500 <= status < 600):
        return ProviderFailure(message, True, "transient")
    if any(token in text or token in name for token in ("timeout", "tempor", "rate limit", "429")):
        return ProviderFailure(message, True, "transient")
    if any(token in text or token in name for token in ("auth", "permission", "401", "403")):
        return ProviderFailure(message, False, "authentication")
    if any(token in text or token in name for token in ("invalid", "bad request", "400")):
        return ProviderFailure(message, False, "request")
    return ProviderFailure(message, False, "unknown")

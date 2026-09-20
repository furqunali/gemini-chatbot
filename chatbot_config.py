"""Configuration helpers for the Gemini chatbot."""

from __future__ import annotations

import os


DEFAULT_MODEL = "gemini-1.5-flash"


def get_api_key() -> str:
    """Return the configured Gemini API key or raise a clear error."""
    value = os.getenv("GEMINI_API_KEY", "").strip()
    if not value:
        raise ValueError(
            "GEMINI_API_KEY is required. Add it to the environment or .env file."
        )
    return value


def get_model_name(override: str | None = None) -> str:
    """Resolve and validate the Gemini model name."""
    if override is not None:
        value = override.strip()
        if not value:
            raise ValueError("GEMINI_MODEL must not be empty.")
        return value

    value = os.getenv("GEMINI_MODEL", "").strip()
    return value or DEFAULT_MODEL

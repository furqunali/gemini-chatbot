"""Validation helpers for interactive chatbot sessions.

These helpers keep user-facing input rules separate from provider calls.
"""
from __future__ import annotations

MAX_PROMPT_LENGTH = 8_000

def validate_prompt(prompt: object) -> str:
    """Normalize a prompt and reject values that cannot be sent safely."""
    if prompt is None:
        return ""
    if not isinstance(prompt, str):
        raise TypeError("prompt must be a string")
    value = prompt.strip()
    if len(value) > MAX_PROMPT_LENGTH:
        raise ValueError(f"prompt must be at most {MAX_PROMPT_LENGTH} characters")
    return value

def is_exit_command(prompt: str) -> bool:
    """Return whether a normalized prompt requests CLI shutdown."""
    return prompt.strip().lower() in {"quit", "exit"}

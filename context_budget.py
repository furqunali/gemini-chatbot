"""Estimate grounded prompt size before provider invocation."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ContextBudget:
    characters: int
    estimated_tokens: int
    limit: int
    within_limit: bool

def estimate_context_budget(text: str, token_limit: int, chars_per_token: float = 4.0) -> ContextBudget:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if token_limit <= 0:
        raise ValueError("token_limit must be positive")
    if chars_per_token <= 0:
        raise ValueError("chars_per_token must be positive")
    characters = len(text)
    tokens = (characters + int(chars_per_token) - 1) // int(chars_per_token)
    return ContextBudget(characters, tokens, token_limit, tokens <= token_limit)

"""Heuristic, tokenizer-free estimates of prompt token counts.

Real tokenizers are model-specific and require heavy dependencies. For budgeting
and guardrail checks a cheap heuristic is usually enough, so this module derives
an estimate from two cheap signals:

* a **character** estimate: ``ceil(len(text) / chars_per_token)``; and
* a **word** estimate: ``ceil(word_count * tokens_per_word)``.

The reported estimate is the larger of the two. Taking the maximum keeps the
heuristic conservative (it rarely under-counts): the character signal dominates
for long, dense words while the word signal dominates for many short words.

Every function here is pure and deterministic -- it depends only on its inputs,
never on wall-clock time, randomness, or a live tokenizer -- mirroring
:mod:`context_budget` and :mod:`conversation_history`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

DEFAULT_CHARS_PER_TOKEN = 4.0
DEFAULT_TOKENS_PER_WORD = 1.3
DEFAULT_PER_MESSAGE_OVERHEAD = 3


@dataclass(frozen=True)
class TokenEstimate:
    """An immutable record of a single heuristic token estimate."""

    characters: int
    words: int
    estimated_tokens: int


def _validate_ratios(chars_per_token: float, tokens_per_word: float) -> None:
    """Reject non-positive tuning ratios up front."""
    if chars_per_token <= 0:
        raise ValueError("chars_per_token must be positive")
    if tokens_per_word <= 0:
        raise ValueError("tokens_per_word must be positive")


def estimate_tokens(
    text: str,
    chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
    tokens_per_word: float = DEFAULT_TOKENS_PER_WORD,
) -> int:
    """Return the heuristic token count of ``text``.

    The estimate is ``max(character_estimate, word_estimate)``. Empty or
    whitespace-free-of-content strings collapse to ``0`` tokens only when they
    contain no characters at all; any non-empty string yields at least ``1``.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    _validate_ratios(chars_per_token, tokens_per_word)
    return estimate(text, chars_per_token, tokens_per_word).estimated_tokens


def estimate(
    text: str,
    chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
    tokens_per_word: float = DEFAULT_TOKENS_PER_WORD,
) -> TokenEstimate:
    """Return a :class:`TokenEstimate` breaking down the heuristic for ``text``."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    _validate_ratios(chars_per_token, tokens_per_word)
    characters = len(text)
    words = len(text.split())
    char_estimate = math.ceil(characters / chars_per_token) if characters else 0
    word_estimate = math.ceil(words * tokens_per_word) if words else 0
    estimated = max(char_estimate, word_estimate)
    return TokenEstimate(characters=characters, words=words, estimated_tokens=estimated)


def estimate_messages_tokens(
    messages: list[dict[str, str]],
    chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
    tokens_per_word: float = DEFAULT_TOKENS_PER_WORD,
    per_message_overhead: int = DEFAULT_PER_MESSAGE_OVERHEAD,
) -> int:
    """Estimate the combined token cost of a list of ``{"content": ...}`` messages.

    Each message contributes the estimate of its ``content`` plus a fixed
    ``per_message_overhead`` accounting for role framing added by chat providers.
    """
    if not isinstance(messages, list):
        raise TypeError("messages must be a list")
    if not isinstance(per_message_overhead, int) or isinstance(per_message_overhead, bool):
        raise TypeError("per_message_overhead must be an int")
    if per_message_overhead < 0:
        raise ValueError("per_message_overhead must not be negative")
    _validate_ratios(chars_per_token, tokens_per_word)

    total = 0
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            raise TypeError(f"messages[{index}] must be a dict")
        if "content" not in message:
            raise ValueError(f"messages[{index}] must have a 'content' key")
        content = message["content"]
        if not isinstance(content, str):
            raise TypeError(f"messages[{index}]['content'] must be a string")
        total += estimate_tokens(content, chars_per_token, tokens_per_word)
        total += per_message_overhead
    return total

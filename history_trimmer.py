"""Trim a conversation history to fit a token budget.

Unlike :class:`conversation_history.ConversationHistory`, which owns and mutates
a running log, this module is a pure transform over a plain list of message
dicts. It always preserves every ``system`` message (they carry standing
instructions that must survive trimming) and keeps as many of the *most recent*
non-system turns as the remaining budget allows, dropping oldest-first.

The token cost of each message is measured by a caller-supplied ``token_counter``
callable. When none is given a character-based estimate identical in spirit to
:mod:`context_budget` is used. Passing the counter in keeps the function pure and
deterministic -- no wall-clock, no randomness, no hidden global tokenizer.
"""

from __future__ import annotations

import math
from typing import Callable, Optional

DEFAULT_CHARS_PER_TOKEN = 4.0
SYSTEM_ROLE = "system"


def _default_counter(chars_per_token: float) -> Callable[[str], int]:
    """Build a character-based token counter using ceiling division."""

    def counter(content: str) -> int:
        return math.ceil(len(content) / chars_per_token) if content else 0

    return counter


def _validate_messages(messages: list[dict[str, str]]) -> None:
    """Ensure ``messages`` is a list of well-formed role/content dicts."""
    if not isinstance(messages, list):
        raise TypeError("messages must be a list")
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            raise TypeError(f"messages[{index}] must be a dict")
        role = message.get("role")
        content = message.get("content")
        if not isinstance(role, str):
            raise TypeError(f"messages[{index}]['role'] must be a string")
        if not isinstance(content, str):
            raise TypeError(f"messages[{index}]['content'] must be a string")


def trim_history(
    messages: list[dict[str, str]],
    max_tokens: int,
    chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
    token_counter: Optional[Callable[[str], int]] = None,
) -> list[dict[str, str]]:
    """Return a trimmed copy of ``messages`` fitting within ``max_tokens``.

    All ``system`` messages are retained regardless of budget. Non-system
    messages are kept from the newest end while the running total stays within
    ``max_tokens``; older ones are dropped first. The original relative ordering
    of the surviving messages is preserved.

    System messages are never dropped even if they alone exceed ``max_tokens``,
    guaranteeing standing instructions always reach the model.
    """
    if not isinstance(max_tokens, int) or isinstance(max_tokens, bool):
        raise TypeError("max_tokens must be an int")
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    if chars_per_token <= 0:
        raise ValueError("chars_per_token must be positive")
    if token_counter is not None and not callable(token_counter):
        raise TypeError("token_counter must be callable")
    _validate_messages(messages)

    counter = token_counter or _default_counter(chars_per_token)

    system_cost = 0
    for message in messages:
        if message["role"] == SYSTEM_ROLE:
            system_cost += counter(message["content"])

    remaining = max_tokens - system_cost
    keep_indices: set[int] = set()

    # Walk non-system messages newest-first, keeping while budget remains.
    for index in range(len(messages) - 1, -1, -1):
        message = messages[index]
        if message["role"] == SYSTEM_ROLE:
            continue
        cost = counter(message["content"])
        if cost <= remaining:
            keep_indices.add(index)
            remaining -= cost
        else:
            break

    result: list[dict[str, str]] = []
    for index, message in enumerate(messages):
        if message["role"] == SYSTEM_ROLE or index in keep_indices:
            result.append(dict(message))
    return result

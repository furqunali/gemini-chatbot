"""System-prompt-aware token estimation and context-window trimming.

This module answers a single, provider-neutral question: *given a system prompt
and a sequence of conversation turns, which turns should I send so the request
fits an approximate token budget?* The system prompt is treated as pinned
context and is **always** retained; only conversation turns are dropped, and
they are dropped from the oldest end first so the most recent exchanges survive.

The token estimate mirrors :mod:`conversation_history` and :mod:`context_budget`:
characters are divided by an approximate ``chars_per_token`` ratio using ceiling
division. An optional ``per_message_overhead`` models the small, fixed number of
tokens a provider spends framing each message (role markers, separators). The
estimate is intentionally cheap and does not depend on any live tokenizer.

Nothing here performs I/O, so it is safe to call from synchronous or asynchronous
code paths alike.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from conversation_history import DEFAULT_CHARS_PER_TOKEN, Turn


def estimate_tokens(
    text: str,
    chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
    per_message_overhead: int = 0,
) -> int:
    """Approximate the token cost of a single message.

    The character count is divided by ``chars_per_token`` using ceiling division
    so that any non-empty text costs at least one token, then ``per_message_overhead``
    is added to account for provider-side role/separator framing.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    _validate_chars_per_token(chars_per_token)
    _validate_overhead(per_message_overhead)
    per_token = max(int(chars_per_token), 1)
    body = (len(text) + per_token - 1) // per_token
    return body + per_message_overhead


@dataclass(frozen=True)
class FittedContext:
    """The result of fitting a system prompt plus turns into a token budget.

    ``turns`` holds the retained conversation turns, oldest first. ``dropped``
    counts how many of the original turns were removed to fit the budget.
    ``within_limit`` is ``False`` only when the pinned system prompt alone already
    exceeds ``token_limit`` -- in that case every turn is dropped but the system
    prompt is still surfaced so the caller can decide how to recover.
    """

    system_prompt: str
    turns: tuple[Turn, ...]
    total_tokens: int
    token_limit: int
    dropped: int
    within_limit: bool

    def messages(self) -> list[dict[str, str]]:
        """Render the fitted context as provider-neutral message mappings.

        A non-empty system prompt is emitted first as a ``system`` message,
        followed by the retained turns in chronological order.
        """
        messages: list[dict[str, str]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.extend(turn.as_message() for turn in self.turns)
        return messages


def fit_context_window(
    system_prompt: str,
    turns: Iterable[Turn],
    token_limit: int,
    chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
    per_message_overhead: int = 0,
) -> FittedContext:
    """Drop oldest turns until the context fits ``token_limit``, keeping the system prompt.

    ``system_prompt`` may be an empty string to indicate "no system prompt"; any
    other value is pinned and never dropped, and it is counted with one message's
    worth of ``per_message_overhead`` when non-empty.

    ``turns`` is any iterable of :class:`~conversation_history.Turn` objects,
    oldest first. Turns are removed from the oldest end until the running total of
    (system prompt + remaining turns) is at or below ``token_limit``. If the system
    prompt alone already exceeds the budget, all turns are dropped and
    ``within_limit`` is ``False``.

    Raises:
        TypeError: if ``system_prompt`` is not a string, ``token_limit`` is not an
            ``int`` (``bool`` rejected), or any element of ``turns`` is not a ``Turn``.
        ValueError: if ``token_limit`` is not positive, ``chars_per_token`` is not
            positive, or ``per_message_overhead`` is negative.
    """
    if not isinstance(system_prompt, str):
        raise TypeError("system_prompt must be a string")
    if not isinstance(token_limit, int) or isinstance(token_limit, bool):
        raise TypeError("token_limit must be an int")
    if token_limit <= 0:
        raise ValueError("token_limit must be positive")
    _validate_chars_per_token(chars_per_token)
    _validate_overhead(per_message_overhead)

    turn_list: list[Turn] = list(turns)
    for index, turn in enumerate(turn_list):
        if not isinstance(turn, Turn):
            raise TypeError(f"turns[{index}] must be a Turn")

    system_tokens = (
        estimate_tokens(system_prompt, chars_per_token, per_message_overhead)
        if system_prompt
        else 0
    )
    turn_tokens = [
        estimate_tokens(turn.content, chars_per_token, per_message_overhead)
        for turn in turn_list
    ]

    original_count = len(turn_list)
    start = 0
    running = system_tokens + sum(turn_tokens)
    # Drop from the oldest end until the total fits or no turns remain.
    while start < original_count and running > token_limit:
        running -= turn_tokens[start]
        start += 1

    kept = tuple(turn_list[start:])
    total_tokens = system_tokens + sum(turn_tokens[start:])
    within_limit = total_tokens <= token_limit
    return FittedContext(
        system_prompt=system_prompt,
        turns=kept,
        total_tokens=total_tokens,
        token_limit=token_limit,
        dropped=start,
        within_limit=within_limit,
    )


def _validate_chars_per_token(chars_per_token: float) -> None:
    if chars_per_token <= 0:
        raise ValueError("chars_per_token must be positive")


def _validate_overhead(per_message_overhead: int) -> None:
    if not isinstance(per_message_overhead, int) or isinstance(per_message_overhead, bool):
        raise TypeError("per_message_overhead must be an int")
    if per_message_overhead < 0:
        raise ValueError("per_message_overhead must not be negative")

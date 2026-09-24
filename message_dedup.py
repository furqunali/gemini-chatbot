"""Collapse consecutive duplicate messages in a conversation history.

Retries, reconnecting clients, and misbehaving upstreams can push the exact same
message into a history twice in a row. This module removes such *consecutive*
duplicates (identical ``role`` and ``content``) while leaving non-adjacent
repeats intact -- a user genuinely asking the same question later in the
conversation is meaningful and must be preserved.

The transform is pure and deterministic: it returns a new list and never mutates
its input. Comparison is exact by default; ``ignore_whitespace`` relaxes it to
ignore leading/trailing whitespace and collapse internal runs when deciding
whether two adjacent messages are duplicates.
"""

from __future__ import annotations


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


def _key(message: dict[str, str], ignore_whitespace: bool) -> tuple[str, str]:
    """Return the comparison key for a message."""
    content = message["content"]
    if ignore_whitespace:
        content = " ".join(content.split())
    return (message["role"], content)


def dedup_consecutive(
    messages: list[dict[str, str]],
    ignore_whitespace: bool = False,
) -> list[dict[str, str]]:
    """Return a copy of ``messages`` with consecutive duplicates collapsed.

    The first message of each run of identical adjacent messages is kept (with
    its original content preserved verbatim, even under ``ignore_whitespace``);
    the following duplicates are dropped. Ordering is otherwise preserved.
    """
    if not isinstance(ignore_whitespace, bool):
        raise TypeError("ignore_whitespace must be a bool")
    _validate_messages(messages)

    result: list[dict[str, str]] = []
    previous_key: tuple[str, str] | None = None
    for message in messages:
        current_key = _key(message, ignore_whitespace)
        if current_key == previous_key:
            continue
        result.append(dict(message))
        previous_key = current_key
    return result


def count_consecutive_duplicates(
    messages: list[dict[str, str]],
    ignore_whitespace: bool = False,
) -> int:
    """Return how many messages ``dedup_consecutive`` would remove."""
    return len(messages) - len(dedup_consecutive(messages, ignore_whitespace))

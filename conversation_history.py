"""Multi-turn conversation history with turn-count and token-budget trimming.

This module keeps a bounded, provider-neutral record of a chat conversation.
Turns are appended as they happen and the history is trimmed from the oldest
end so that it never exceeds either a maximum number of turns or an approximate
token budget. The trimmed view is exposed as a plain list of ``{"role", "content"}``
message dicts suitable for building the next prompt.

The token estimate mirrors :mod:`context_budget`: characters are divided by an
approximate ``chars_per_token`` ratio using ceiling division. It is deliberately
provider-agnostic and does not depend on any live tokenizer.
"""

from __future__ import annotations

from dataclasses import dataclass

VALID_ROLES = ("user", "assistant")
DEFAULT_CHARS_PER_TOKEN = 4.0


def _estimate_tokens(text: str, chars_per_token: float) -> int:
    """Approximate the token count of ``text`` via ceiling division."""
    per_token = int(chars_per_token)
    per_token = max(per_token, 1)
    return (len(text) + per_token - 1) // per_token


@dataclass(frozen=True)
class Turn:
    """A single, validated conversation turn from ``user`` or ``assistant``."""

    role: str
    content: str

    def __post_init__(self) -> None:
        if not isinstance(self.role, str):
            raise TypeError("role must be a string")
        if self.role not in VALID_ROLES:
            raise ValueError(f"role must be one of {VALID_ROLES}")
        if not isinstance(self.content, str):
            raise TypeError("content must be a string")
        if not self.content.strip():
            raise ValueError("content must not be empty")

    def estimated_tokens(self, chars_per_token: float = DEFAULT_CHARS_PER_TOKEN) -> int:
        """Return the approximate token cost of this turn's content."""
        return _estimate_tokens(self.content, chars_per_token)

    def as_message(self) -> dict[str, str]:
        """Render the turn as a provider-neutral message mapping."""
        return {"role": self.role, "content": self.content}


class ConversationHistory:
    """A bounded conversation log trimmed by turn count and token budget.

    Turns are stored newest-last. After every append the log is trimmed from the
    oldest end until it satisfies both ``max_turns`` and ``max_tokens``. The most
    recent turn is always retained so the next prompt is never empty, even if that
    turn alone exceeds the token budget.
    """

    def __init__(
        self,
        max_turns: int,
        max_tokens: int,
        chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
    ) -> None:
        if not isinstance(max_turns, int) or isinstance(max_turns, bool):
            raise TypeError("max_turns must be an int")
        if not isinstance(max_tokens, int) or isinstance(max_tokens, bool):
            raise TypeError("max_tokens must be an int")
        if max_turns <= 0:
            raise ValueError("max_turns must be positive")
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if chars_per_token <= 0:
            raise ValueError("chars_per_token must be positive")
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.chars_per_token = chars_per_token
        self._turns: list[Turn] = []

    def __len__(self) -> int:
        return len(self._turns)

    @property
    def turns(self) -> tuple[Turn, ...]:
        """Return the retained turns, oldest first, as an immutable tuple."""
        return tuple(self._turns)

    def append(self, role: str, content: str) -> Turn:
        """Append a turn for ``role`` and trim the history to its limits."""
        turn = Turn(role, content.strip() if isinstance(content, str) else content)
        self._turns.append(turn)
        self._trim()
        return turn

    def append_user(self, content: str) -> Turn:
        """Append a user turn and trim the history."""
        return self.append("user", content)

    def append_assistant(self, content: str) -> Turn:
        """Append an assistant turn and trim the history."""
        return self.append("assistant", content)

    def total_tokens(self) -> int:
        """Return the approximate token cost of all retained turns."""
        return sum(t.estimated_tokens(self.chars_per_token) for t in self._turns)

    def messages(self) -> list[dict[str, str]]:
        """Return the trimmed turns as message dicts for the next prompt."""
        return [t.as_message() for t in self._turns]

    def clear(self) -> None:
        """Drop all retained turns."""
        self._turns.clear()

    def _trim(self) -> None:
        """Drop oldest turns until within ``max_turns`` and ``max_tokens``."""
        if len(self._turns) > self.max_turns:
            del self._turns[: len(self._turns) - self.max_turns]
        while len(self._turns) > 1 and self.total_tokens() > self.max_tokens:
            self._turns.pop(0)

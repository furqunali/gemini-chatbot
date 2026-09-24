"""Compute per-turn and cumulative token costs for a conversation.

Providers bill separately for prompt (input) and completion (output) tokens at a
per-1,000-token rate. Given the token counts of each turn and those two rates,
this module produces an immutable :class:`TurnCost` per turn and a
:class:`CostReport` aggregating them, so a caller can show both a running total
and a per-turn breakdown.

All computation is pure and deterministic. Costs are rounded to a fixed number of
decimal places (``ndigits``) so equal inputs always yield byte-identical floats,
avoiding floating-point noise in comparisons and display.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

DEFAULT_NDIGITS = 6


@dataclass(frozen=True)
class TurnCost:
    """Immutable cost breakdown for a single turn."""

    prompt_tokens: int
    completion_tokens: int
    prompt_cost: float
    completion_cost: float
    total_cost: float

    @property
    def total_tokens(self) -> int:
        """Return the combined prompt and completion token count."""
        return self.prompt_tokens + self.completion_tokens


@dataclass(frozen=True)
class CostReport:
    """Immutable aggregate over a sequence of :class:`TurnCost` records."""

    turns: tuple[TurnCost, ...]
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost: float

    @property
    def total_tokens(self) -> int:
        """Return the combined token count across all turns."""
        return self.total_prompt_tokens + self.total_completion_tokens


def _check_tokens(value: int, label: str) -> None:
    """Reject non-int / negative token counts."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{label} must be an int")
    if value < 0:
        raise ValueError(f"{label} must not be negative")


def _check_rate(value: float, label: str) -> None:
    """Reject non-numeric / negative rates."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a number")
    if value < 0:
        raise ValueError(f"{label} must not be negative")


def _check_ndigits(ndigits: int) -> None:
    if not isinstance(ndigits, int) or isinstance(ndigits, bool):
        raise TypeError("ndigits must be an int")
    if ndigits < 0:
        raise ValueError("ndigits must not be negative")


def cost_for_turn(
    prompt_tokens: int,
    completion_tokens: int,
    prompt_rate_per_1k: float,
    completion_rate_per_1k: float,
    ndigits: int = DEFAULT_NDIGITS,
) -> TurnCost:
    """Return the :class:`TurnCost` for one turn.

    Cost of a token bucket is ``tokens / 1000 * rate_per_1k``, rounded to
    ``ndigits`` decimal places.
    """
    _check_tokens(prompt_tokens, "prompt_tokens")
    _check_tokens(completion_tokens, "completion_tokens")
    _check_rate(prompt_rate_per_1k, "prompt_rate_per_1k")
    _check_rate(completion_rate_per_1k, "completion_rate_per_1k")
    _check_ndigits(ndigits)

    prompt_cost = round(prompt_tokens / 1000 * prompt_rate_per_1k, ndigits)
    completion_cost = round(completion_tokens / 1000 * completion_rate_per_1k, ndigits)
    total_cost = round(prompt_cost + completion_cost, ndigits)
    return TurnCost(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        prompt_cost=prompt_cost,
        completion_cost=completion_cost,
        total_cost=total_cost,
    )


def build_cost_report(
    turns: Iterable[tuple[int, int]],
    prompt_rate_per_1k: float,
    completion_rate_per_1k: float,
    ndigits: int = DEFAULT_NDIGITS,
) -> CostReport:
    """Aggregate a sequence of ``(prompt_tokens, completion_tokens)`` pairs.

    Each pair becomes a :class:`TurnCost`; the report sums token counts and
    costs across all turns. The cumulative ``total_cost`` is rounded to
    ``ndigits`` after summation.
    """
    if isinstance(turns, (str, bytes, dict)):
        raise TypeError("turns must be an iterable of (prompt, completion) pairs")
    _check_rate(prompt_rate_per_1k, "prompt_rate_per_1k")
    _check_rate(completion_rate_per_1k, "completion_rate_per_1k")
    _check_ndigits(ndigits)

    turn_costs: list[TurnCost] = []
    for index, pair in enumerate(turns):
        try:
            prompt_tokens, completion_tokens = pair
        except (TypeError, ValueError):
            raise ValueError(
                f"turns[{index}] must be a (prompt_tokens, completion_tokens) pair"
            )
        turn_costs.append(
            cost_for_turn(
                prompt_tokens,
                completion_tokens,
                prompt_rate_per_1k,
                completion_rate_per_1k,
                ndigits,
            )
        )

    total_prompt = sum(t.prompt_tokens for t in turn_costs)
    total_completion = sum(t.completion_tokens for t in turn_costs)
    total_cost = round(sum(t.total_cost for t in turn_costs), ndigits)
    return CostReport(
        turns=tuple(turn_costs),
        total_prompt_tokens=total_prompt,
        total_completion_tokens=total_completion,
        total_cost=total_cost,
    )

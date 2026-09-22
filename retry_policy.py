"""Bounded retry policy for transient model-provider failures."""
from __future__ import annotations

import asyncio
import math
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    """Configuration for bounded exponential-backoff retries."""

    max_attempts: int = 3
    base_delay: float = 0.25
    max_delay: float = 4.0
    jitter: float = 0.1

    def __post_init__(self) -> None:
        if not isinstance(self.max_attempts, int) or isinstance(self.max_attempts, bool) or self.max_attempts < 1:
            raise ValueError("max_attempts must be a positive integer")
        for name, value in (("base_delay", self.base_delay), ("max_delay", self.max_delay), ("jitter", self.jitter)):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"{name} must be numeric")  # noqa: TRY004 - public API contract raises ValueError for all config errors
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.base_delay < 0 or self.max_delay < 0:
            raise ValueError("delays must be non-negative")
        if self.max_delay < self.base_delay:
            raise ValueError("max_delay must be >= base_delay")
        if not 0 <= self.jitter <= 1:
            raise ValueError("jitter must be between 0 and 1")

    def delay_for(self, retry_number: int, random_value: float = 0.5) -> float:
        """Return a deterministic-compatible delay for a retry number."""
        if not isinstance(retry_number, int) or isinstance(retry_number, bool) or retry_number < 1:
            raise ValueError("retry_number must be a positive integer")
        if (not isinstance(random_value, (int, float)) or isinstance(random_value, bool) or not math.isfinite(random_value)):
            raise ValueError("random_value must be a finite number")
        if not 0 <= random_value <= 1:
            raise ValueError("random_value must be between 0 and 1")
        if self.base_delay == 0:
            exponential = 0.0
        else:
            max_exponent = max(0, math.ceil(math.log2(self.max_delay) - math.log2(self.base_delay)))
            exponent = min(retry_number - 1, max_exponent)
            exponential = min(self.max_delay, self.base_delay * (2 ** exponent))
        spread = exponential * self.jitter
        return max(0.0, min(self.max_delay, exponential - spread + 2 * spread * random_value))


async def run_with_retry(
    operation: Callable[[], Awaitable[T]],
    policy: RetryPolicy,
    retryable: Callable[[Exception], bool] | None = None,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    random_value: Callable[[], float] = random.random,
) -> T:
    """Run an async operation with bounded retries and exponential backoff."""
    if not callable(operation):
        raise TypeError("operation must be callable")
    if retryable is None:
        retryable = lambda exc: True

    last_error: Exception | None = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return await operation()
        except Exception as exc:
            last_error = exc
            if attempt >= policy.max_attempts or not retryable(exc):
                raise
            await sleep(policy.delay_for(attempt, random_value()))

    raise RuntimeError(f"retry loop exited unexpectedly: {last_error}")

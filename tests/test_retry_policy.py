import asyncio

import pytest

from retry_policy import RetryPolicy, run_with_retry


def test_policy_validation_and_backoff():
    policy = RetryPolicy(max_attempts=3, base_delay=1, max_delay=4, jitter=0)
    assert policy.delay_for(1, 0.5) == 1
    assert policy.delay_for(3, 0.5) == 4


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_attempts": 0},
        {"base_delay": -1},
        {"max_delay": 0, "base_delay": 1},
        {"jitter": 1.1},
    ],
)
def test_invalid_policy(kwargs):
    with pytest.raises(ValueError):
        RetryPolicy(**kwargs)


def test_retry_succeeds_after_transient_failures():
    calls = 0
    delays = []

    async def operation():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise RuntimeError("temporary")
        return "ok"

    async def sleep(delay):
        delays.append(delay)

    result = asyncio.run(
        run_with_retry(operation, RetryPolicy(max_attempts=3, base_delay=1, jitter=0), sleep=sleep)
    )
    assert result == "ok"
    assert calls == 3
    assert delays == [1, 2]


def test_non_retryable_error_is_immediate():
    calls = 0

    async def operation():
        nonlocal calls
        calls += 1
        raise ValueError("permanent")

    async def sleep(_):
        raise AssertionError("should not sleep")

    with pytest.raises(ValueError):
        asyncio.run(
            run_with_retry(
                operation,
                RetryPolicy(max_attempts=4),
                retryable=lambda exc: not isinstance(exc, ValueError),
                sleep=sleep,
            )
        )
    assert calls == 1


def test_invalid_retry_policy_types():
    with pytest.raises(ValueError, match="positive integer"):
        RetryPolicy(max_attempts=2.5)
    with pytest.raises(ValueError, match="positive integer"):
        RetryPolicy(max_attempts=True)
    with pytest.raises(ValueError, match="numeric"):
        RetryPolicy(base_delay="1")

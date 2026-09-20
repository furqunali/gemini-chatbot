import pytest

from chatbot_errors import ProviderError
from chatbot_service import EMPTY_RESPONSE, ChatService, normalize_prompt
from retry_policy import RetryPolicy


def test_normalize_prompt_handles_missing_and_whitespace():
    assert normalize_prompt(None) == ""
    assert normalize_prompt("  hello  ") == "hello"


@pytest.mark.asyncio
async def test_generate_returns_prompt_message_for_blank_input():
    service = ChatService(object())
    assert await service.generate("   ") == "Please enter a message."


@pytest.mark.asyncio
async def test_generate_strips_provider_response():
    class Model:
        async def generate_content_async(self, prompt):
            assert prompt == "hello"
            return type("Response", (), {"text": "  answer  "})()
    assert await ChatService(Model()).generate("  hello ") == "answer"


@pytest.mark.asyncio
async def test_generate_returns_empty_response_message():
    class Model:
        async def generate_content_async(self, prompt):
            return type("Response", (), {"text": "   "})()
    assert await ChatService(Model()).generate("hello") == EMPTY_RESPONSE


@pytest.mark.asyncio
async def test_generate_wraps_provider_failure():
    class Model:
        async def generate_content_async(self, prompt):
            raise RuntimeError("network")
    with pytest.raises(ProviderError, match="network"):
        await ChatService(Model()).generate("hello")


@pytest.mark.asyncio
async def test_generate_retries_rate_limit_then_succeeds():
    calls = 0
    delays = []

    class RateLimitError(Exception):
        status_code = 429

    class Model:
        async def generate_content_async(self, prompt):
            nonlocal calls
            calls += 1
            if calls < 2:
                raise RateLimitError("busy")
            return type("Response", (), {"text": "ok"})()

    async def sleep(delay):
        delays.append(delay)

    policy = RetryPolicy(max_attempts=2, base_delay=0, jitter=0)
    service = ChatService(Model(), retry_policy=policy)
    service.retry_policy = policy

    import retry_policy as retry_module
    result = await retry_module.run_with_retry(
        lambda: service.model.generate_content_async("hello"),
        policy,
        retryable=lambda exc: getattr(exc, "status_code", None) == 429,
        sleep=sleep,
    )
    assert result.text == "ok"
    assert calls == 2
    assert delays == [0]


@pytest.mark.asyncio
async def test_generate_does_not_retry_client_error():
    calls = 0

    class ClientError(Exception):
        status_code = 400

    class Model:
        async def generate_content_async(self, prompt):
            nonlocal calls
            calls += 1
            raise ClientError("bad request")

    with pytest.raises(ProviderError, match="bad request"):
        await ChatService(Model(), retry_policy=RetryPolicy(max_attempts=3)).generate("hello")
    assert calls == 1

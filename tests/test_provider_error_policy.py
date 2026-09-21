from provider_error_policy import classify_provider_error


def test_timeout_is_retryable():
    result = classify_provider_error(TimeoutError("request timed out"))
    assert result.retryable
    assert result.category == "transient"


def test_authentication_failure_is_not_retryable():
    result = classify_provider_error(RuntimeError("401 unauthorized"))
    assert not result.retryable
    assert result.category == "authentication"


def test_invalid_request_is_not_retryable():
    result = classify_provider_error(ValueError("400 bad request"))
    assert not result.retryable
    assert result.category == "request"


def test_unknown_error_is_conservative():
    result = classify_provider_error(RuntimeError("provider exploded"))
    assert not result.retryable
    assert result.category == "unknown"


def test_structured_rate_limit_status_is_retryable():
    class RateLimitError(Exception):
        status_code = 429

    result = classify_provider_error(RateLimitError("quota exceeded"))
    assert result.retryable
    assert result.category == "transient"


def test_structured_server_status_is_retryable():
    class ServerError(Exception):
        status_code = 503

    result = classify_provider_error(ServerError("service unavailable"))
    assert result.retryable
    assert result.category == "transient"


def test_wrapped_provider_status_is_retryable():
    class ServerError(Exception):
        status_code = 503

    wrapped = RuntimeError("provider wrapper")
    wrapped.__cause__ = ServerError("service unavailable")
    result = classify_provider_error(wrapped)
    assert result.retryable
    assert result.category == "transient"


def test_deeply_wrapped_provider_status_is_retryable():
    class ServerError(Exception):
        status_code = 503

    inner = ServerError("service unavailable")
    middle = RuntimeError("provider wrapper")
    middle.__cause__ = inner
    outer = RuntimeError("transport wrapper")
    outer.__cause__ = middle
    result = classify_provider_error(outer)
    assert result.retryable
    assert result.category == "transient"

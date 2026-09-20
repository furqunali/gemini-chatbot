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

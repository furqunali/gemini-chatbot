import pytest

from chatbot_errors import ChatbotError, ConfigurationError, ProviderError


def test_chatbot_error_is_base_exception():
    assert issubclass(ChatbotError, Exception)


def test_configuration_error_is_chatbot_and_value_error():
    assert issubclass(ConfigurationError, ChatbotError)
    assert issubclass(ConfigurationError, ValueError)


def test_provider_error_is_chatbot_error():
    assert issubclass(ProviderError, ChatbotError)


def test_errors_preserve_message():
    assert str(ConfigurationError("missing key")) == "missing key"
    assert str(ProviderError("provider failed")) == "provider failed"

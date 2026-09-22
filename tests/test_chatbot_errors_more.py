from chatbot_errors import ChatbotError, ConfigurationError, ProviderError


def test_configuration_error_is_chatbot_error():
    error = ConfigurationError("missing key")
    assert isinstance(error, ChatbotError)
    assert str(error) == "missing key"

def test_provider_error_is_chatbot_error():
    error = ProviderError("provider failed")
    assert isinstance(error, ChatbotError)
    assert str(error) == "provider failed"

def test_errors_preserve_empty_message():
    assert str(ChatbotError()) == ""
    assert str(ConfigurationError()) == ""
    assert str(ProviderError()) == ""

def test_error_classes_are_distinct():
    assert ChatbotError is not ConfigurationError
    assert ChatbotError is not ProviderError

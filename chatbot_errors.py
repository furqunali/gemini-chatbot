"""Domain errors for chatbot configuration and provider failures."""
class ChatbotError(Exception):
    """Base exception for recoverable chatbot failures."""

class ConfigurationError(ChatbotError, ValueError):
    """Raised when required chatbot configuration is missing or invalid."""

class ProviderError(ChatbotError):
    """Raised when the configured model provider cannot answer."""

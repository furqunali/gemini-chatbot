
from chatbot_protocol import response_text


def test_response_text_strips_provider_text():
    response = type("Response", (), {"text": "  hello  "})()
    assert response_text(response) == "hello"


def test_response_text_returns_empty_for_missing_text():
    assert response_text(object()) == ""


def test_response_text_returns_empty_for_non_string_text():
    response = type("Response", (), {"text": None})()
    assert response_text(response) == ""


def test_async_text_model_contract_is_importable():
    from chatbot_protocol import AsyncTextModel

    assert AsyncTextModel is not None

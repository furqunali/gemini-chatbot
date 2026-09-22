from chatbot_protocol import response_text


def test_response_text_preserves_internal_spacing():
    response = type("Response", (), {"text": "hello   world"})()
    assert response_text(response) == "hello   world"

def test_response_text_strips_newlines():
    response = type("Response", (), {"text": "\nhello\n"})()
    assert response_text(response) == "hello"

def test_response_text_rejects_list_text_as_empty():
    response = type("Response", (), {"text": ["hello"]})()
    assert response_text(response) == ""

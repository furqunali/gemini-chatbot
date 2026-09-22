import pytest

from request_context import RequestContext, new_request_context


def test_new_context_has_unique_id():
    first = new_request_context(component="chat")
    second = new_request_context(component="chat")
    assert first.request_id != second.request_id
    assert first.metadata == {"component": "chat"}


def test_context_can_add_metadata_without_mutation():
    original = RequestContext("req-1", {"component": "chat"})
    updated = original.with_metadata(provider="gemini")
    assert original.metadata == {"component": "chat"}
    assert updated.metadata == {"component": "chat", "provider": "gemini"}


def test_context_rejects_invalid_request_id():
    with pytest.raises(ValueError):
        RequestContext(" ")


def test_context_rejects_non_string_metadata_values():
    with pytest.raises(TypeError):
        RequestContext("req-1", {"attempt": 1})

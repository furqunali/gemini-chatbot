import pytest

from response_envelope import ResponseEnvelope, from_text


def test_envelope_normalizes_provider_metadata():
    result = from_text("  answer  ", provider=" gemini ", model="test", grounded=True,
                       citations=["source#1"], metadata={"latency_ms": 12})
    assert result.text == "answer"
    assert result.provider == "gemini"
    assert result.citations == ("source#1",)
    assert result.as_dict()["citations"] == ["source#1"]


@pytest.mark.parametrize("kwargs", [
    {"text": ""},
    {"text": "ok", "provider": ""},
    {"text": "ok", "citations": ("",)},
])
def test_invalid_envelopes_are_rejected(kwargs):
    with pytest.raises((ValueError, TypeError)):
        ResponseEnvelope(**kwargs)

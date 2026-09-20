import pytest

from response_envelope import ResponseEnvelope
from response_metadata import with_metadata


def test_with_metadata_preserves_existing_values():
    envelope = ResponseEnvelope("answer", provider="gemini", metadata={"request_id": "r1"})
    updated = with_metadata(envelope, latency_ms=42)
    assert envelope.metadata == {"request_id": "r1"}
    assert updated.metadata == {"request_id": "r1", "latency_ms": 42}


def test_with_metadata_overrides_named_values():
    envelope = ResponseEnvelope("answer", metadata={"mode": "draft"})
    assert with_metadata(envelope, mode="final").metadata["mode"] == "final"


def test_with_metadata_requires_valid_envelope():
    with pytest.raises(ValueError):
        ResponseEnvelope("")

"""Safe metadata composition for provider responses."""
from __future__ import annotations

from typing import Any

from response_envelope import ResponseEnvelope


def with_metadata(envelope: ResponseEnvelope, **values: Any) -> ResponseEnvelope:
    """Return a new envelope while preserving existing response metadata."""
    merged = {**envelope.metadata, **values}
    return ResponseEnvelope(
        text=envelope.text,
        provider=envelope.provider,
        model=envelope.model,
        grounded=envelope.grounded,
        citations=envelope.citations,
        metadata=merged,
    )

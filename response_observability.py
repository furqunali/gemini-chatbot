"""Compact response metrics for provider-neutral chatbot observability."""
from __future__ import annotations
from dataclasses import dataclass
from response_envelope import ResponseEnvelope

@dataclass(frozen=True)
class ResponseMetrics:
    characters: int
    citations: int
    grounded: bool
    provider: str

def measure_response(envelope: ResponseEnvelope) -> ResponseMetrics:
    return ResponseMetrics(
        characters=len(envelope.text),
        citations=len(envelope.citations),
        grounded=envelope.grounded,
        provider=envelope.provider,
    )

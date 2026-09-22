"""Provider-neutral response policy for grounded chatbot output."""
from __future__ import annotations

from dataclasses import dataclass

from response_envelope import ResponseEnvelope


@dataclass(frozen=True)
class ResponsePolicy:
    require_grounding: bool = False
    require_citations_when_grounded: bool = True
    min_citations: int = 1

    def validate(self) -> ResponsePolicy:
        if self.min_citations < 0:
            raise ValueError("min_citations must be non-negative")
        return self

def validate_response(envelope: ResponseEnvelope, policy: ResponsePolicy) -> ResponseEnvelope:
    policy.validate()
    if policy.require_grounding and not envelope.grounded:
        raise ValueError("grounding is required")
    if envelope.grounded and policy.require_citations_when_grounded and len(envelope.citations) < policy.min_citations:
        raise ValueError("grounded responses require citations")
    return envelope

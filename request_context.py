"""Provider-neutral request context for correlating chatbot operations."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True)
class RequestContext:
    request_id: str
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id must be non-empty")
        if any(not isinstance(k, str) or not k.strip() for k in self.metadata):
            raise ValueError("metadata keys must be non-empty strings")
        if any(not isinstance(v, str) for v in self.metadata.values()):
            raise TypeError("metadata values must be strings")

    def with_metadata(self, **values: str) -> RequestContext:
        if any(not isinstance(v, str) for v in values.values()):
            raise TypeError("metadata values must be strings")
        merged = {**self.metadata, **values}
        return RequestContext(self.request_id, merged)


def new_request_context(**metadata: str) -> RequestContext:
    """Create a unique request context for one end-to-end operation."""
    return RequestContext(str(uuid4()), dict(metadata))

"""Provider-neutral response metadata for chatbot integrations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ResponseEnvelope:
    text: str
    provider: str = "unknown"
    model: str | None = None
    grounded: bool = False
    citations: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError("text must be a string")
        if not self.text.strip():
            raise ValueError("text must be non-empty")
        if not isinstance(self.provider, str) or not self.provider.strip():
            raise ValueError("provider must be non-empty")
        if any(not isinstance(citation, str) or not citation.strip() for citation in self.citations):
            raise ValueError("citations must contain non-empty strings")

    def as_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "provider": self.provider,
            "model": self.model,
            "grounded": self.grounded,
            "citations": list(self.citations),
            "metadata": dict(self.metadata),
        }

def from_text(text: str, *, provider: str = "unknown", model: str | None = None,
              grounded: bool = False, citations: list[str] | tuple[str, ...] = (),
              metadata: dict[str, Any] | None = None) -> ResponseEnvelope:
    return ResponseEnvelope(
        text=text.strip(), provider=provider.strip(), model=model,
        grounded=grounded, citations=tuple(citations), metadata=dict(metadata or {}),
    )

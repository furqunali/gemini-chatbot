"""Provider-neutral evidence summary for grounded responses."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceSummary:
    citation_count: int
    unique_citations: tuple[str, ...]
    grounded: bool

def summarize_evidence(citations: list[str] | tuple[str, ...], grounded: bool) -> EvidenceSummary:
    normalized=tuple(sorted({str(value).strip() for value in citations if str(value).strip()}))
    return EvidenceSummary(len(citations), normalized, grounded)

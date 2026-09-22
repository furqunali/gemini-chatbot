"""Stable formatting for citations attached to provider responses."""
from __future__ import annotations


def format_citations(citations: tuple[str, ...] | list[str]) -> str:
    normalized=sorted({str(value).strip() for value in citations if str(value).strip()})
    return " ".join(f"[{value}]" for value in normalized)

def append_citations(text: str, citations: tuple[str, ...] | list[str]) -> str:
    base=text.rstrip()
    suffix=format_citations(citations)
    return f"{base} {suffix}".strip() if suffix else base

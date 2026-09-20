"""Provider-neutral formatting for grounded generation context."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ContextItem:
    source: str
    text: str
    index: int

def build_grounded_prompt(question: str, items: list[ContextItem]) -> str:
    question = (question or "").strip()
    if not question:
        raise ValueError("question must not be empty")
    if not items:
        raise ValueError("at least one context item is required")
    blocks = []
    for item in items:
        source = item.source.strip()
        text = item.text.strip()
        if not source or not text or item.index < 0:
            raise ValueError("context items must contain valid source, text and index")
        blocks.append(f"[SOURCE {item.index}] {source}\n{text}")
    return (
        "Answer the question using only the supplied sources. "
        "If the sources do not contain enough information, say so explicitly. "
        "Do not invent citations.\n\n"
        + "\n\n".join(blocks)
        + f"\n\nQUESTION: {question}"
    )

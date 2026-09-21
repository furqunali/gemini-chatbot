"""Deterministic status counts for response execution traces."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from response_trace import ResponseTrace

@dataclass(frozen=True)
class TraceStatusSummary:
    events: int
    completed: int
    failed: int
    errors: int
    other: int
    terminal_status: str | None

def summarize_trace_status(trace: ResponseTrace) -> TraceStatusSummary:
    counts=Counter(event.status.lower() for event in trace.events)
    return TraceStatusSummary(len(trace.events), counts["completed"], counts["failed"],
        counts["error"], sum(n for s,n in counts.items() if s not in {"completed","failed","error"}),
        trace.events[-1].status.lower() if trace.events else None)

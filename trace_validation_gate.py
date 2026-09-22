"""Deterministic validation gate for response execution traces."""
from __future__ import annotations

from dataclasses import dataclass

from response_trace import ResponseTrace


@dataclass(frozen=True)
class TraceValidation:
    events: int
    blank_details: int
    passed: bool

def validate_trace(trace: ResponseTrace) -> TraceValidation:
    if not isinstance(trace, ResponseTrace):
        raise TypeError("trace must be a ResponseTrace")
    blank_details = sum(not event.detail.strip() for event in trace.events)
    return TraceValidation(len(trace.events), blank_details, bool(trace.events) and trace.events[-1].status.lower() == "completed")

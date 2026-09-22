"""Deterministic health classification for response execution traces."""
from __future__ import annotations

from dataclasses import dataclass

from response_trace import ResponseTrace


@dataclass(frozen=True)
class TraceHealth:
    status: str
    event_count: int
    failed_events: int
    completed: bool

def assess_trace(trace: ResponseTrace) -> TraceHealth:
    failed = sum(event.status in {"failed", "error"} for event in trace.events)
    if failed:
        status = "failed"
    elif trace.completed:
        status = "completed"
    else:
        status = "incomplete"
    return TraceHealth(status, len(trace.events), failed, trace.completed)

"""Aggregate deterministic response trace health metrics."""
from __future__ import annotations
from dataclasses import dataclass
from response_trace_health import TraceHealth

@dataclass(frozen=True)
class TraceSummary:
    events: int
    failed: int
    completed: bool
    status: str

def summarize_trace(health: TraceHealth) -> TraceSummary:
    return TraceSummary(
        events=health.event_count,
        failed=health.failed_events,
        completed=health.completed,
        status=health.status,
    )

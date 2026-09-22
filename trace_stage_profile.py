"""Deterministic stage statistics for response execution traces."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from response_trace import ResponseTrace


@dataclass(frozen=True)
class TraceStageProfile:
    stages: tuple[str, ...]
    event_count: int
    repeated_stages: tuple[str, ...]
    statuses: tuple[str, ...]
    failed_events: int

def profile_trace_stages(trace: ResponseTrace) -> TraceStageProfile:
    stage_counts = Counter(event.stage for event in trace.events)
    status_counts = Counter(event.status for event in trace.events)
    return TraceStageProfile(tuple(sorted(stage_counts)), len(trace.events), tuple(sorted(s for s, n in stage_counts.items() if n > 1)), tuple(sorted(status_counts)), sum(event.status.lower() in {"failed", "error"} for event in trace.events))

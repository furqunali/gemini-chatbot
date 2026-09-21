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

def profile_trace_stages(trace: ResponseTrace) -> TraceStageProfile:
    counts = Counter(event.stage for event in trace.events)
    return TraceStageProfile(tuple(sorted(counts)), len(trace.events), tuple(sorted(s for s, n in counts.items() if n > 1)))

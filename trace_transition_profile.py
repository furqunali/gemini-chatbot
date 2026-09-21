"""Deterministic transition metrics for response traces."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from response_trace import ResponseTrace

@dataclass(frozen=True)
class TraceTransitionProfile:
    transitions: tuple[tuple[str, str], ...]
    transition_count: int
    repeated_transitions: tuple[tuple[str, str], ...]

def profile_trace_transitions(trace: ResponseTrace) -> TraceTransitionProfile:
    pairs = list(zip(trace.events, trace.events[1:]))
    counts = Counter((left.stage, right.stage) for left, right in pairs)
    return TraceTransitionProfile(
        tuple(sorted(counts)),
        len(pairs),
        tuple(sorted(pair for pair, count in counts.items() if count > 1)),
    )

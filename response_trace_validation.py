"""Deterministic validation for response execution traces."""
from __future__ import annotations

from response_trace import ResponseTrace

_ALLOWED = {"ok", "completed", "failed", "error"}

def validate_trace(trace: ResponseTrace) -> tuple[str, ...]:
    issues: list[str] = []
    if not trace.events:
        issues.append("trace must contain events")
        return tuple(issues)
    terminal_seen = False
    for index, event in enumerate(trace.events):
        if not event.stage.strip():
            issues.append(f"event {index} stage is empty")
        if event.status not in _ALLOWED:
            issues.append(f"event {index} has invalid status")
        if terminal_seen:
            issues.append("events follow a terminal status")
        if event.status in {"completed", "failed", "error"}:
            terminal_seen = True
    return tuple(dict.fromkeys(issues))

def is_valid_trace(trace: ResponseTrace) -> bool:
    return not validate_trace(trace)

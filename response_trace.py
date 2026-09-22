"""Structured, provider-neutral response execution trace."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TraceEvent:
    stage: str
    status: str
    detail: str = ""

@dataclass(frozen=True)
class ResponseTrace:
    request_id: str
    events: tuple[TraceEvent, ...]

    @property
    def completed(self) -> bool:
        return bool(self.events) and self.events[-1].status == "completed"

def build_trace(request_id: str, events: list[TraceEvent] | tuple[TraceEvent, ...]) -> ResponseTrace:
    if not request_id.strip():
        raise ValueError("request_id must not be empty")
    if not events:
        raise ValueError("at least one trace event is required")
    return ResponseTrace(request_id, tuple(events))

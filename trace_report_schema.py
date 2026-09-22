"""Schema validation for exported trace validation reports."""
from __future__ import annotations

REQUIRED_FIELDS = frozenset({"events", "blank_details", "passed"})


def validate_trace_report(payload: dict) -> bool:
    if not isinstance(payload, dict) or set(payload) != REQUIRED_FIELDS:
        return False
    if not isinstance(payload["passed"], bool):
        return False
    return all(
        type(payload[name]) is int and payload[name] >= 0
        for name in ("events", "blank_details")
    )

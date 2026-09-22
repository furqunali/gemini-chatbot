"""Stable JSON contract for response trace health."""
from __future__ import annotations

import json
from dataclasses import asdict

from response_trace_health import TraceHealth


def to_json(health: TraceHealth) -> str:
    return json.dumps(asdict(health), sort_keys=True, separators=(",", ":"))

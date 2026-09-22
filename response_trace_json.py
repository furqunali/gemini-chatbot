"""Stable JSON serialization for response execution traces."""
from __future__ import annotations
from dataclasses import asdict
import json
from response_trace import ResponseTrace

def to_json(trace: ResponseTrace) -> str:
    return json.dumps(asdict(trace), sort_keys=True, separators=(",", ":"))

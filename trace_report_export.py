"""Stable JSON export for response-trace validation results."""
from __future__ import annotations
import json
from dataclasses import asdict
from trace_validation_gate import TraceValidation

def trace_report_dict(result: TraceValidation) -> dict:
    if not isinstance(result, TraceValidation):
        raise TypeError("result must be a TraceValidation")
    return asdict(result)

def trace_report_json(result: TraceValidation) -> str:
    return json.dumps(trace_report_dict(result), sort_keys=True)

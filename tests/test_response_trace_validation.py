from response_trace import TraceEvent, build_trace
from response_trace_validation import is_valid_trace, validate_trace

def test_trace_validation_accepts_non_terminal_progression():
    trace = build_trace("req-4", [TraceEvent("retrieve", "ok"), TraceEvent("generate", "completed")])
    assert is_valid_trace(trace)

def test_trace_validation_rejects_events_after_terminal_status():
    trace = build_trace("req-5", [TraceEvent("generate", "completed"), TraceEvent("audit", "ok")])
    issues = validate_trace(trace)
    assert "events follow a terminal status" in issues

def test_trace_validation_rejects_unknown_status():
    trace = build_trace("req-6", [TraceEvent("generate", "mystery")])
    assert "event 0 has invalid status" in validate_trace(trace)

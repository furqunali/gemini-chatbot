from response_trace import TraceEvent, build_trace
from response_trace_health import assess_trace

def test_trace_health_detects_failed_event():
    trace = build_trace("req-2", [TraceEvent("retrieve", "ok"), TraceEvent("generate", "failed")])
    health = assess_trace(trace)
    assert health.status == "failed"
    assert health.failed_events == 1

def test_trace_health_marks_completed_trace():
    trace = build_trace("req-3", [TraceEvent("generate", "completed")])
    health = assess_trace(trace)
    assert health.status == "completed"
    assert health.completed

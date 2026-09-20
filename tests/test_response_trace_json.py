from response_trace import TraceEvent, build_trace
from response_trace_json import to_json

def test_trace_json_preserves_event_order():
    trace = build_trace("req-1", [TraceEvent("retrieve", "ok"), TraceEvent("generate", "completed")])
    assert to_json(trace) == '{"events":[{"detail":"","stage":"retrieve","status":"ok"},{"detail":"","stage":"generate","status":"completed"}],"request_id":"req-1"}'

import pytest
from response_trace import TraceEvent, build_trace

def test_trace_preserves_stage_order():
    trace = build_trace("req-1", [TraceEvent("retrieve", "ok"), TraceEvent("generate", "completed")])
    assert [event.stage for event in trace.events] == ["retrieve", "generate"]
    assert trace.completed

def test_trace_requires_request_id_and_events():
    with pytest.raises(ValueError):
        build_trace("", [TraceEvent("generate", "completed")])
    with pytest.raises(ValueError):
        build_trace("req-1", [])

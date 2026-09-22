from response_trace_health import TraceHealth
from response_trace_health_json import to_json

def test_trace_health_json_is_stable():
    health = TraceHealth("completed", 3, 0, True)
    assert to_json(health) == '{"completed":true,"event_count":3,"failed_events":0,"status":"completed"}'

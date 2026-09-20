from response_trace_health import TraceHealth
from response_trace_summary import summarize_trace

def test_trace_summary_preserves_health_contract():
    health = TraceHealth("failed", 4, 2, False)
    assert summarize_trace(health) == (4, 2, False, "failed")

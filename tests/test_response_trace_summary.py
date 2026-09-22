from response_trace_health import TraceHealth
from response_trace_summary import summarize_trace


def test_trace_summary_preserves_health_contract():
    health = TraceHealth("failed", 4, 2, False)
    summary = summarize_trace(health)
    assert summary.events == 4
    assert summary.failed == 2
    assert not summary.completed
    assert summary.status == "failed"

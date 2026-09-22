from response_trace import ResponseTrace, TraceEvent
from trace_validation_gate import validate_trace


def test_completed_trace_passes():
    result = validate_trace(ResponseTrace("r", (TraceEvent("answer", "completed", "ok"),)))
    assert result.passed and result.blank_details == 0

def test_failed_trace_does_not_pass():
    result = validate_trace(ResponseTrace("r", (TraceEvent("answer", "failed", "reason"),)))
    assert not result.passed

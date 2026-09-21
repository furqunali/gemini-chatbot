from response_trace import ResponseTrace, TraceEvent
from trace_status_summary import summarize_trace_status

def test_counts_statuses():
    result=summarize_trace_status(ResponseTrace("r",(TraceEvent("a","ok"),TraceEvent("b","completed"),TraceEvent("c","error"))))
    assert result.events == 3 and result.completed == 1 and result.errors == 1
    assert result.terminal_status == "error"

def test_empty_trace():
    assert summarize_trace_status(ResponseTrace("r",())).terminal_status is None

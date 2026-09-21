from response_trace import TraceEvent, build_trace
from trace_stage_profile import profile_trace_stages

def test_stage_profile_is_sorted_and_detects_repeats():
    trace = build_trace("req-7", [TraceEvent("generate","ok"), TraceEvent("retrieve","ok"), TraceEvent("generate","completed")])
    p = profile_trace_stages(trace)
    assert p.stages == ("generate","retrieve")
    assert p.event_count == 3
    assert p.repeated_stages == ("generate",)

def test_stage_profile_handles_single_event():
    trace = build_trace("req-8", [TraceEvent("audit","ok")])
    assert profile_trace_stages(trace).repeated_stages == ()

from response_trace import TraceEvent, build_trace
from trace_transition_profile import profile_trace_transitions


def test_transition_profile_reports_ordered_stage_pairs():
    trace = build_trace("req-1", [TraceEvent("retrieve","ok"),TraceEvent("generate","ok"),TraceEvent("retrieve","ok")])
    p = profile_trace_transitions(trace)
    assert p.transitions == (("generate","retrieve"),("retrieve","generate"))
    assert p.transition_count == 2
    assert p.repeated_transitions == ()

def test_transition_profile_counts_repeated_pairs():
    trace = build_trace("req-2", [TraceEvent("a","ok"),TraceEvent("b","ok"),TraceEvent("a","ok"),TraceEvent("b","ok")])
    assert profile_trace_transitions(trace).repeated_transitions == (("a","b"),)

def test_transition_profile_handles_single_event():
    trace = build_trace("req-3", [TraceEvent("only","ok")])
    assert profile_trace_transitions(trace).transition_count == 0

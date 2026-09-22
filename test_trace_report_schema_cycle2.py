from trace_report_schema import validate_trace_report


def test_trace_report_rejects_blank_details_above_events():
    payload = {"events": 1, "blank_details": 2, "passed": False}
    assert not validate_trace_report(payload)

def test_trace_report_requires_events_for_pass():
    payload = {"events": 0, "blank_details": 0, "passed": True}
    assert not validate_trace_report(payload)

def test_trace_report_rejects_negative_events():
    payload = {"events": -1, "blank_details": 0, "passed": False}
    assert not validate_trace_report(payload)

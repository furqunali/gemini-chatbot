from trace_report_export import trace_report_dict, trace_report_json
from trace_validation_gate import TraceValidation


def test_trace_export_is_deterministic():
    result = TraceValidation(2, 1, False)
    assert trace_report_dict(result) == {"events": 2, "blank_details": 1, "passed": False}
    assert trace_report_json(result) == '{"blank_details": 1, "events": 2, "passed": false}'


def test_trace_export_rejects_wrong_type():
    try:
        trace_report_dict({})
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError")


def test_export_enforces_schema():
    assert trace_report_dict(TraceValidation(1, 0, True))["events"] == 1

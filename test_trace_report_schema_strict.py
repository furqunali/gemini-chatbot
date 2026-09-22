from trace_report_schema import validate_trace_report


def _valid_report() -> dict:
    return {"events": 2, "blank_details": 0, "passed": True}


def test_schema_rejects_bool_as_count():
    payload = _valid_report()
    payload["events"] = True
    assert not validate_trace_report(payload)


def test_schema_accepts_zero_counts():
    assert validate_trace_report(_valid_report())

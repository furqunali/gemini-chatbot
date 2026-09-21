from trace_report_schema import validate_trace_report

def test_valid_trace_schema():
    assert validate_trace_report({"events":2,"blank_details":0,"passed":True})

def test_negative_count_fails():
    assert not validate_trace_report({"events":-1,"blank_details":0,"passed":True})

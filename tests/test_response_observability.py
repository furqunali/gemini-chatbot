from response_envelope import ResponseEnvelope
from response_observability import measure_response

def test_measure_response_reports_grounding_and_citations():
    metrics=measure_response(ResponseEnvelope("answer",provider="gemini",grounded=True,citations=("c1","c2")))
    assert metrics.characters==6
    assert metrics.citations==2
    assert metrics.grounded
    assert metrics.provider=="gemini"

def test_measure_response_handles_plain_response():
    assert measure_response(ResponseEnvelope("ok")).characters==2

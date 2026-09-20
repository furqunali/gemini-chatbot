import pytest
from response_envelope import ResponseEnvelope
from response_policy import ResponsePolicy, validate_response

def test_grounded_response_requires_citations():
    envelope = ResponseEnvelope("answer", grounded=True)
    with pytest.raises(ValueError):
        validate_response(envelope, ResponsePolicy())

def test_ungrounded_response_can_pass():
    envelope = ResponseEnvelope("answer", grounded=False)
    assert validate_response(envelope, ResponsePolicy()) is envelope

def test_policy_can_require_grounding():
    envelope = ResponseEnvelope("answer", grounded=False)
    with pytest.raises(ValueError):
        validate_response(envelope, ResponsePolicy(require_grounding=True))

def test_policy_rejects_negative_minimum():
    with pytest.raises(ValueError):
        ResponsePolicy(min_citations=-1).validate()

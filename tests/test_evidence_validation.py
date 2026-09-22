from evidence_validation import evidence_issues, is_valid_evidence
from response_evidence import EvidenceSummary


def test_grounded_response_requires_citations():
    summary=EvidenceSummary(0,(),True)
    assert evidence_issues(summary)==("grounded response has no citations",)
    assert not is_valid_evidence(summary)

def test_valid_grounded_evidence():
    assert is_valid_evidence(EvidenceSummary(2,("a",),True))

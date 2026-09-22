from response_evidence import summarize_evidence


def test_summary_normalizes_unique_citations():
    summary=summarize_evidence(["b","a","b"],True)
    assert summary.citation_count==3
    assert summary.unique_citations==("a","b")
    assert summary.grounded is True

def test_summary_handles_empty_evidence():
    summary=summarize_evidence([],False)
    assert summary.citation_count==0
    assert summary.unique_citations==()

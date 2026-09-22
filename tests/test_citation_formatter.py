from citation_formatter import append_citations, format_citations


def test_format_citations_is_deterministic():
    assert format_citations(["b","a","a"])=="[a] [b]"

def test_append_citations_handles_empty_values():
    assert append_citations("answer",["","c1"])=="answer [c1]"

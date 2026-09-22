"""Validation rules for grounded response evidence."""
from __future__ import annotations

from response_evidence import EvidenceSummary


def evidence_issues(summary: EvidenceSummary) -> tuple[str, ...]:
    issues=[]
    if summary.citation_count < 0:
        issues.append("negative citation count")
    if summary.grounded and not summary.unique_citations:
        issues.append("grounded response has no citations")
    if summary.citation_count < len(summary.unique_citations):
        issues.append("unique citation count exceeds total count")
    return tuple(issues)

def is_valid_evidence(summary: EvidenceSummary) -> bool:
    return not evidence_issues(summary)

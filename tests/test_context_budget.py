import pytest

from context_budget import estimate_context_budget


def test_budget_estimation():
    result=estimate_context_budget("a"*10, 3)
    assert result.characters == 10
    assert result.estimated_tokens == 3
    assert result.within_limit

def test_budget_validation():
    with pytest.raises(ValueError):
        estimate_context_budget("x", 0)
    with pytest.raises(ValueError):
        estimate_context_budget("x", 2, 0)

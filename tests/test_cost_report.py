import pytest

from cost_report import CostReport, TurnCost, build_cost_report, cost_for_turn


def test_cost_for_turn_basic():
    turn = cost_for_turn(1000, 500, prompt_rate_per_1k=0.5, completion_rate_per_1k=1.5)
    assert turn.prompt_cost == 0.5
    assert turn.completion_cost == 0.75
    assert turn.total_cost == 1.25


def test_turn_total_tokens_property():
    turn = cost_for_turn(1200, 300, prompt_rate_per_1k=0, completion_rate_per_1k=0)
    assert turn.total_tokens == 1500


def test_zero_tokens_zero_cost():
    turn = cost_for_turn(0, 0, prompt_rate_per_1k=10, completion_rate_per_1k=10)
    assert turn.total_cost == 0.0


def test_turn_record_is_frozen():
    turn = cost_for_turn(10, 10, prompt_rate_per_1k=1, completion_rate_per_1k=1)
    with pytest.raises(AttributeError):
        turn.total_cost = 0  # type: ignore[misc]


def test_rounding_applied():
    # 333/1000 * 1 = 0.333 exactly; force fewer digits.
    turn = cost_for_turn(333, 0, prompt_rate_per_1k=1, completion_rate_per_1k=1, ndigits=2)
    assert turn.prompt_cost == 0.33


def test_build_report_aggregates():
    report = build_cost_report(
        [(1000, 500), (2000, 1000)],
        prompt_rate_per_1k=1.0,
        completion_rate_per_1k=2.0,
    )
    assert isinstance(report, CostReport)
    assert len(report.turns) == 2
    assert report.total_prompt_tokens == 3000
    assert report.total_completion_tokens == 1500
    # turn1: 1.0 + 1.0 = 2.0 ; turn2: 2.0 + 2.0 = 4.0
    assert report.total_cost == 6.0


def test_report_total_tokens_property():
    report = build_cost_report(
        [(100, 50)], prompt_rate_per_1k=1, completion_rate_per_1k=1
    )
    assert report.total_tokens == 150


def test_build_report_empty():
    report = build_cost_report([], prompt_rate_per_1k=1, completion_rate_per_1k=1)
    assert report.turns == ()
    assert report.total_cost == 0.0
    assert report.total_prompt_tokens == 0


def test_report_record_is_frozen():
    report = build_cost_report([], prompt_rate_per_1k=1, completion_rate_per_1k=1)
    with pytest.raises(AttributeError):
        report.total_cost = 5  # type: ignore[misc]


def test_accepts_generator_of_pairs():
    report = build_cost_report(
        ((n, n) for n in (1000, 1000)),
        prompt_rate_per_1k=1,
        completion_rate_per_1k=1,
    )
    assert report.total_cost == 4.0


def test_token_validation():
    with pytest.raises(TypeError, match="prompt_tokens must be an int"):
        cost_for_turn(True, 0, prompt_rate_per_1k=1, completion_rate_per_1k=1)
    with pytest.raises(ValueError, match="completion_tokens must not be negative"):
        cost_for_turn(0, -1, prompt_rate_per_1k=1, completion_rate_per_1k=1)


def test_rate_validation():
    with pytest.raises(TypeError, match="prompt_rate_per_1k must be a number"):
        cost_for_turn(0, 0, prompt_rate_per_1k="x", completion_rate_per_1k=1)
    with pytest.raises(ValueError, match="completion_rate_per_1k must not be negative"):
        cost_for_turn(0, 0, prompt_rate_per_1k=1, completion_rate_per_1k=-1)


def test_ndigits_validation():
    with pytest.raises(ValueError, match="ndigits must not be negative"):
        cost_for_turn(0, 0, prompt_rate_per_1k=1, completion_rate_per_1k=1, ndigits=-1)


def test_build_report_pair_validation():
    with pytest.raises(ValueError, match=r"turns\[0\] must be a"):
        build_cost_report([(1, 2, 3)], prompt_rate_per_1k=1, completion_rate_per_1k=1)
    with pytest.raises(TypeError, match="turns must be an iterable"):
        build_cost_report({"a": 1}, prompt_rate_per_1k=1, completion_rate_per_1k=1)

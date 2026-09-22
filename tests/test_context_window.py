import pytest

from context_window import FittedContext, estimate_tokens, fit_context_window
from conversation_history import Turn

# --- estimate_tokens -------------------------------------------------------

def test_estimate_tokens_ceiling_division():
    # chars_per_token=4 => 8 chars -> 2 tokens, 9 chars -> 3 tokens.
    assert estimate_tokens("a" * 8, chars_per_token=4.0) == 2
    assert estimate_tokens("a" * 9, chars_per_token=4.0) == 3


def test_estimate_tokens_empty_string_is_zero():
    assert estimate_tokens("", chars_per_token=4.0) == 0


def test_estimate_tokens_overhead_added():
    assert estimate_tokens("a" * 8, chars_per_token=4.0, per_message_overhead=3) == 5
    # Overhead applies even to empty content.
    assert estimate_tokens("", chars_per_token=4.0, per_message_overhead=3) == 3


def test_estimate_tokens_validation():
    with pytest.raises(TypeError, match="text must be a string"):
        estimate_tokens(123)
    with pytest.raises(ValueError, match="chars_per_token must be positive"):
        estimate_tokens("hi", chars_per_token=0)
    with pytest.raises(ValueError, match="per_message_overhead must not be negative"):
        estimate_tokens("hi", per_message_overhead=-1)
    with pytest.raises(TypeError, match="per_message_overhead must be an int"):
        estimate_tokens("hi", per_message_overhead=True)


# --- fit_context_window: happy paths --------------------------------------

def test_everything_fits_no_drops():
    turns = [Turn("user", "a" * 4), Turn("assistant", "b" * 4)]
    fitted = fit_context_window("sys", turns, token_limit=1000, chars_per_token=1)
    assert fitted.dropped == 0
    assert [t.content for t in fitted.turns] == ["a" * 4, "b" * 4]
    # 3 (sys) + 4 + 4 = 11 tokens with chars_per_token=1.
    assert fitted.total_tokens == 11
    assert fitted.within_limit is True


def test_drops_oldest_turns_to_fit():
    # chars_per_token=1 => tokens == characters. system "sys" = 3 tokens.
    turns = [Turn("user", "a" * 5), Turn("assistant", "b" * 5), Turn("user", "c" * 5)]
    # Budget 13: 3 + 5 + 5 + 5 = 18 -> drop oldest (a) -> 3 + 5 + 5 = 13.
    fitted = fit_context_window("sys", turns, token_limit=13, chars_per_token=1)
    assert fitted.dropped == 1
    assert [t.content for t in fitted.turns] == ["b" * 5, "c" * 5]
    assert fitted.total_tokens == 13
    assert fitted.within_limit is True


def test_system_prompt_always_kept_even_when_all_turns_dropped():
    turns = [Turn("user", "a" * 20), Turn("assistant", "b" * 20)]
    # Budget only fits the system prompt (3 tokens) with room to spare but not a turn.
    fitted = fit_context_window("sys", turns, token_limit=4, chars_per_token=1)
    assert fitted.dropped == 2
    assert fitted.turns == ()
    assert fitted.total_tokens == 3
    assert fitted.within_limit is True
    assert fitted.messages() == [{"role": "system", "content": "sys"}]


def test_system_prompt_alone_exceeds_budget_marks_not_within_limit():
    turns = [Turn("user", "hello")]
    fitted = fit_context_window("s" * 50, turns, token_limit=10, chars_per_token=1)
    assert fitted.dropped == 1
    assert fitted.turns == ()
    assert fitted.total_tokens == 50
    assert fitted.within_limit is False
    # System prompt is still surfaced for caller recovery.
    assert fitted.messages() == [{"role": "system", "content": "s" * 50}]


def test_empty_system_prompt_is_omitted_from_messages():
    turns = [Turn("user", "hi")]
    fitted = fit_context_window("", turns, token_limit=1000, chars_per_token=1)
    assert fitted.total_tokens == 2
    assert fitted.messages() == [{"role": "user", "content": "hi"}]


def test_empty_turns_returns_only_system():
    fitted = fit_context_window("sys", [], token_limit=100, chars_per_token=1)
    assert fitted.turns == ()
    assert fitted.dropped == 0
    assert fitted.total_tokens == 3
    assert fitted.within_limit is True


def test_overhead_counts_per_message_and_can_force_a_drop():
    # chars_per_token=1, overhead=2 per message. system "s" = 1 + 2 = 3.
    turns = [Turn("user", "a" * 3), Turn("user", "b" * 3)]
    # Per turn: 3 + 2 = 5. Total = 3 + 5 + 5 = 13.
    # Budget 8 -> drop oldest -> 3 + 5 = 8.
    fitted = fit_context_window(
        "s", turns, token_limit=8, chars_per_token=1, per_message_overhead=2
    )
    assert fitted.dropped == 1
    assert [t.content for t in fitted.turns] == ["b" * 3]
    assert fitted.total_tokens == 8
    assert fitted.within_limit is True


def test_accepts_any_iterable_of_turns():
    def gen():
        yield Turn("user", "a")
        yield Turn("assistant", "b")

    fitted = fit_context_window("", gen(), token_limit=100, chars_per_token=1)
    assert [t.content for t in fitted.turns] == ["a", "b"]


def test_messages_shape_and_order():
    turns = [Turn("user", "q"), Turn("assistant", "r")]
    fitted = fit_context_window("sys", turns, token_limit=100, chars_per_token=1)
    assert fitted.messages() == [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "q"},
        {"role": "assistant", "content": "r"},
    ]


# --- fit_context_window: validation ---------------------------------------

def test_fit_validation_errors():
    turns = [Turn("user", "hi")]
    with pytest.raises(TypeError, match="system_prompt must be a string"):
        fit_context_window(None, turns, token_limit=10)
    with pytest.raises(TypeError, match="token_limit must be an int"):
        fit_context_window("sys", turns, token_limit=True)
    with pytest.raises(ValueError, match="token_limit must be positive"):
        fit_context_window("sys", turns, token_limit=0)
    with pytest.raises(ValueError, match="chars_per_token must be positive"):
        fit_context_window("sys", turns, token_limit=10, chars_per_token=0)
    with pytest.raises(ValueError, match="per_message_overhead must not be negative"):
        fit_context_window("sys", turns, token_limit=10, per_message_overhead=-1)


def test_fit_rejects_non_turn_elements():
    with pytest.raises(TypeError, match=r"turns\[1\] must be a Turn"):
        fit_context_window(
            "sys", [Turn("user", "ok"), {"role": "user", "content": "bad"}], token_limit=10
        )


def test_fitted_context_is_immutable():
    fitted = fit_context_window("sys", [], token_limit=10)
    assert isinstance(fitted, FittedContext)
    with pytest.raises(AttributeError):
        fitted.total_tokens = 5  # type: ignore[misc]

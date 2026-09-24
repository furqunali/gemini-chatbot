import pytest

from history_trimmer import trim_history


def _msg(role, content):
    return {"role": role, "content": content}


def test_keeps_everything_when_within_budget():
    messages = [_msg("user", "hi"), _msg("assistant", "hello")]
    assert trim_history(messages, max_tokens=1000) == messages


def test_drops_oldest_non_system_first():
    # chars_per_token=1 => tokens == characters.
    messages = [
        _msg("user", "a" * 6),
        _msg("assistant", "b" * 6),
        _msg("user", "c" * 6),
    ]
    # budget 12 keeps the two most recent (6 + 6), drops the oldest.
    trimmed = trim_history(messages, max_tokens=12, chars_per_token=1)
    assert [m["content"] for m in trimmed] == ["b" * 6, "c" * 6]


def test_system_message_always_retained():
    messages = [
        _msg("system", "s" * 6),
        _msg("user", "a" * 6),
        _msg("assistant", "b" * 6),
    ]
    # budget only fits the system + newest turn.
    trimmed = trim_history(messages, max_tokens=12, chars_per_token=1)
    assert trimmed[0]["role"] == "system"
    assert [m["content"] for m in trimmed] == ["s" * 6, "b" * 6]


def test_system_kept_even_when_it_exceeds_budget():
    messages = [_msg("system", "s" * 50), _msg("user", "a" * 4)]
    trimmed = trim_history(messages, max_tokens=5, chars_per_token=1)
    # System survives; no room left for the user turn.
    assert trimmed == [_msg("system", "s" * 50)]


def test_original_order_preserved():
    messages = [
        _msg("system", "sys"),
        _msg("user", "u1"),
        _msg("system", "sys2"),
        _msg("assistant", "a1"),
    ]
    trimmed = trim_history(messages, max_tokens=1000)
    assert trimmed == messages


def test_stops_at_first_turn_that_does_not_fit():
    messages = [
        _msg("user", "a" * 20),   # too big, older
        _msg("assistant", "b" * 4),
        _msg("user", "c" * 4),
    ]
    # budget 8 fits the two newest; the older 20-char turn does not fit and
    # trimming stops there rather than skipping it.
    trimmed = trim_history(messages, max_tokens=8, chars_per_token=1)
    assert [m["content"] for m in trimmed] == ["b" * 4, "c" * 4]


def test_returns_new_list_and_copies():
    messages = [_msg("user", "hi")]
    trimmed = trim_history(messages, max_tokens=100)
    assert trimmed is not messages
    assert trimmed[0] is not messages[0]


def test_custom_token_counter_used():
    messages = [_msg("user", "x"), _msg("assistant", "y")]
    # Counter charging 10 tokens each; budget 10 fits only the newest.
    trimmed = trim_history(messages, max_tokens=10, token_counter=lambda c: 10)
    assert [m["content"] for m in trimmed] == ["y"]


def test_empty_history():
    assert trim_history([], max_tokens=100) == []


def test_max_tokens_validation():
    with pytest.raises(TypeError, match="max_tokens must be an int"):
        trim_history([], max_tokens=True)
    with pytest.raises(ValueError, match="max_tokens must be positive"):
        trim_history([], max_tokens=0)


def test_chars_per_token_validation():
    with pytest.raises(ValueError, match="chars_per_token must be positive"):
        trim_history([], max_tokens=10, chars_per_token=0)


def test_token_counter_must_be_callable():
    with pytest.raises(TypeError, match="token_counter must be callable"):
        trim_history([], max_tokens=10, token_counter=123)  # type: ignore[arg-type]


def test_message_structure_validation():
    with pytest.raises(TypeError, match="messages must be a list"):
        trim_history("nope", max_tokens=10)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"messages\[0\]\['role'\] must be a string"):
        trim_history([{"content": "hi"}], max_tokens=10)
    with pytest.raises(TypeError, match=r"messages\[0\]\['content'\] must be a string"):
        trim_history([{"role": "user", "content": 5}], max_tokens=10)  # type: ignore[dict-item]

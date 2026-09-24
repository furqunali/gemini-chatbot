import pytest

from message_dedup import count_consecutive_duplicates, dedup_consecutive


def _msg(role, content):
    return {"role": role, "content": content}


def test_collapses_adjacent_identical():
    messages = [_msg("user", "hi"), _msg("user", "hi"), _msg("assistant", "yo")]
    assert dedup_consecutive(messages) == [_msg("user", "hi"), _msg("assistant", "yo")]


def test_keeps_non_adjacent_repeats():
    messages = [
        _msg("user", "hi"),
        _msg("assistant", "yo"),
        _msg("user", "hi"),
    ]
    assert dedup_consecutive(messages) == messages


def test_same_content_different_role_not_duplicate():
    messages = [_msg("user", "ping"), _msg("assistant", "ping")]
    assert dedup_consecutive(messages) == messages


def test_collapses_long_run():
    messages = [_msg("user", "x")] * 5
    assert dedup_consecutive(messages) == [_msg("user", "x")]


def test_returns_new_list_and_copies():
    messages = [_msg("user", "hi")]
    result = dedup_consecutive(messages)
    assert result is not messages
    assert result[0] is not messages[0]


def test_empty_list():
    assert dedup_consecutive([]) == []


def test_no_duplicates_unchanged():
    messages = [_msg("user", "a"), _msg("assistant", "b"), _msg("user", "c")]
    assert dedup_consecutive(messages) == messages


def test_ignore_whitespace_treats_as_duplicate():
    messages = [_msg("user", "hi  there"), _msg("user", "hi there ")]
    # Exact comparison keeps both.
    assert len(dedup_consecutive(messages)) == 2
    # Whitespace-insensitive comparison collapses them.
    collapsed = dedup_consecutive(messages, ignore_whitespace=True)
    assert collapsed == [_msg("user", "hi  there")]  # first kept verbatim


def test_ignore_whitespace_preserves_original_content():
    messages = [_msg("user", "  a  "), _msg("user", "a")]
    collapsed = dedup_consecutive(messages, ignore_whitespace=True)
    assert collapsed[0]["content"] == "  a  "


def test_count_consecutive_duplicates():
    messages = [_msg("user", "x"), _msg("user", "x"), _msg("user", "x")]
    assert count_consecutive_duplicates(messages) == 2


def test_count_zero_when_unique():
    messages = [_msg("user", "a"), _msg("user", "b")]
    assert count_consecutive_duplicates(messages) == 0


def test_ignore_whitespace_type_validation():
    with pytest.raises(TypeError, match="ignore_whitespace must be a bool"):
        dedup_consecutive([], ignore_whitespace="yes")  # type: ignore[arg-type]


def test_message_structure_validation():
    with pytest.raises(TypeError, match="messages must be a list"):
        dedup_consecutive("nope")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"messages\[0\] must be a dict"):
        dedup_consecutive([1])  # type: ignore[list-item]
    with pytest.raises(TypeError, match=r"messages\[0\]\['role'\] must be a string"):
        dedup_consecutive([{"content": "hi"}])
    with pytest.raises(TypeError, match=r"messages\[0\]\['content'\] must be a string"):
        dedup_consecutive([{"role": "user", "content": 5}])  # type: ignore[dict-item]

import pytest

from chatbot_validation import MAX_PROMPT_LENGTH, is_exit_command, validate_prompt


def test_validate_prompt_preserves_internal_whitespace():
    assert validate_prompt("  hello   world  ") == "hello   world"


def test_validate_prompt_accepts_maximum_length():
    value = "x" * MAX_PROMPT_LENGTH
    assert validate_prompt(value) == value


def test_validate_prompt_rejects_one_over_maximum():
    with pytest.raises(ValueError, match="at most"):
        validate_prompt("x" * (MAX_PROMPT_LENGTH + 1))


def test_validate_prompt_rejects_non_string_values():
    with pytest.raises(TypeError, match="must be a string"):
        validate_prompt(123)


def test_is_exit_command_ignores_case_and_whitespace():
    assert is_exit_command("  EXIT  ")
    assert is_exit_command("quit")
    assert not is_exit_command("exit now")

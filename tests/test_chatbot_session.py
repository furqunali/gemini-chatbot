import pytest

from chatbot_validation import is_exit_command, validate_prompt


def test_validate_prompt_normalizes_whitespace():
    assert validate_prompt("  hello  ") == "hello"


def test_validate_prompt_rejects_non_string_values():
    with pytest.raises(ValueError, match="must be a string"):
        validate_prompt(None)


def test_validate_prompt_rejects_oversized_prompts():
    with pytest.raises(ValueError, match="too long"):
        validate_prompt("x" * 8001)


def test_is_exit_command_is_case_insensitive():
    assert is_exit_command("  EXIT  ")
    assert is_exit_command("quit")
    assert not is_exit_command("continue")

import pytest
from chatbot_validation import validate_prompt, is_exit_command, MAX_PROMPT_LENGTH

def test_validate_prompt_keeps_unicode_text():
    assert validate_prompt("  hello 🌍  ") == "hello 🌍"

def test_validate_prompt_allows_empty_string():
    assert validate_prompt("") == ""

def test_validate_prompt_rejects_long_unicode_input():
    with pytest.raises(ValueError):
        validate_prompt("x" * (MAX_PROMPT_LENGTH + 1))

def test_exit_command_accepts_mixed_case():
    assert is_exit_command("ExIt")

def test_exit_command_rejects_empty_input():
    assert not is_exit_command("")

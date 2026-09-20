from cli import build_parser
from chatbot_validation import is_exit_command, validate_prompt

def test_cli_parser_accepts_one_shot_prompt():
    args=build_parser().parse_args(["--prompt","hello","--model","test-model"])
    assert args.prompt=="hello"
    assert args.model=="test-model"

def test_cli_exit_commands_are_case_insensitive():
    assert is_exit_command(" EXIT ")
    assert is_exit_command("quit")

def test_cli_prompt_validation_rejects_non_strings():
    try:
        validate_prompt(123)
    except TypeError:
        pass
    else:
        raise AssertionError("non-string prompt should fail")

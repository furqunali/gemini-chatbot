import pytest

from cli import build_parser, build_service, run_once
from chatbot_validation import is_exit_command, validate_prompt


class FakeModel:
    async def generate_content_async(self, prompt):
        return type("Response", (), {"text": f"reply:{prompt}"})()


def test_cli_parser_accepts_one_shot_prompt():
    args = build_parser().parse_args(["--prompt", "hello", "--model", "test-model"])
    assert args.prompt == "hello"
    assert args.model == "test-model"


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


def test_build_service_returns_chat_service(monkeypatch):
    monkeypatch.setattr("cli.get_api_key", lambda: "test-key")
    monkeypatch.setattr("cli.build_model", lambda api_key, model_name: FakeModel())

    service = build_service("test-model")

    assert service.model.__class__.__name__ == "FakeModel"


@pytest.mark.asyncio
async def test_run_once_uses_sync_service_builder(monkeypatch):
    monkeypatch.setattr("cli.build_service", lambda model_name: __import__(
        "chatbot_service"
    ).ChatService(FakeModel()))

    assert await run_once(" hello ", "test-model") == "reply:hello"

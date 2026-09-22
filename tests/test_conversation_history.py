import pytest

from chatbot_service import ChatService
from conversation_history import ConversationHistory, Turn


def test_turn_validation():
    with pytest.raises(ValueError, match="role must be one of"):
        Turn("system", "hi")
    with pytest.raises(ValueError, match="content must not be empty"):
        Turn("user", "   ")
    with pytest.raises(TypeError, match="content must be a string"):
        Turn("user", 123)
    with pytest.raises(TypeError, match="role must be a string"):
        Turn(None, "hi")


def test_turn_token_estimate_and_message():
    turn = Turn("user", "a" * 8)
    assert turn.estimated_tokens(chars_per_token=4.0) == 2
    assert turn.as_message() == {"role": "user", "content": "a" * 8}


def test_history_constructor_validation():
    with pytest.raises(ValueError, match="max_turns must be positive"):
        ConversationHistory(0, 100)
    with pytest.raises(ValueError, match="max_tokens must be positive"):
        ConversationHistory(4, 0)
    with pytest.raises(ValueError, match="chars_per_token must be positive"):
        ConversationHistory(4, 100, chars_per_token=0)
    with pytest.raises(TypeError, match="max_turns must be an int"):
        ConversationHistory(True, 100)


def test_append_normalizes_and_builds_messages():
    history = ConversationHistory(max_turns=10, max_tokens=1000)
    history.append_user("  hello  ")
    history.append_assistant("  hi there  ")
    assert history.messages() == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi there"},
    ]
    assert len(history) == 2


def test_trim_by_max_turns_keeps_most_recent():
    history = ConversationHistory(max_turns=2, max_tokens=10_000)
    history.append_user("one")
    history.append_assistant("two")
    history.append_user("three")
    contents = [m["content"] for m in history.messages()]
    assert contents == ["two", "three"]
    assert len(history) == 2


def test_trim_by_token_budget_drops_oldest():
    # chars_per_token=1 => tokens == characters. Budget of 10 chars.
    history = ConversationHistory(max_turns=100, max_tokens=10, chars_per_token=1)
    history.append_user("a" * 6)
    history.append_assistant("b" * 6)  # total 12 > 10 -> drop the first
    assert [m["content"] for m in history.messages()] == ["b" * 6]
    assert history.total_tokens() == 6


def test_single_oversized_turn_is_retained():
    history = ConversationHistory(max_turns=100, max_tokens=5, chars_per_token=1)
    history.append_user("x" * 50)
    # Cannot trim below one turn even though it exceeds the budget.
    assert len(history) == 1
    assert history.messages() == [{"role": "user", "content": "x" * 50}]


def test_both_limits_applied_together():
    history = ConversationHistory(max_turns=3, max_tokens=6, chars_per_token=1)
    for i in range(5):
        history.append_user(f"{i}" * 3)  # 3 tokens each
    # max_turns caps at 3 turns (9 tokens), then token budget (6) drops one more.
    contents = [m["content"] for m in history.messages()]
    assert contents == ["3" * 3, "4" * 3]
    assert history.total_tokens() == 6


def test_clear_and_turns_property():
    history = ConversationHistory(max_turns=5, max_tokens=100)
    history.append_user("hi")
    assert isinstance(history.turns, tuple)
    assert history.turns[0].role == "user"
    history.clear()
    assert len(history) == 0
    assert history.messages() == []


class _EchoModel:
    """Fake async model that echoes the last user message it is given."""

    def __init__(self) -> None:
        self.seen: list[str] = []

    async def generate_content_async(self, prompt: str):
        self.seen.append(prompt)

        class _Resp:
            text = f"echo: {prompt}"

        return _Resp()


async def test_history_feeds_service_prompt():
    history = ConversationHistory(max_turns=4, max_tokens=1000)
    history.append_user("first question")
    history.append_assistant("first answer")
    history.append_user("second question")

    rendered = "\n".join(f"{m['role']}: {m['content']}" for m in history.messages())
    model = _EchoModel()
    service = ChatService(model)
    reply = await service.generate(rendered)

    assert model.seen[0] == rendered
    assert "second question" in reply
    history.append_assistant(reply)
    assert history.turns[-1].role == "assistant"

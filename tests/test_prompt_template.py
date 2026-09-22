from dataclasses import FrozenInstanceError

import pytest

from chatbot_service import ChatService
from prompt_template import (
    MissingVariablesError,
    PromptTemplate,
    TemplateError,
    UnknownVariablesError,
    escape_value,
)


def test_variables_are_detected_in_first_seen_order():
    tpl = PromptTemplate("Hi {name}, your order {order} for {name} is ready.")
    assert tpl.variables == ("name", "order")


def test_template_with_no_slots_renders_verbatim():
    tpl = PromptTemplate("just a plain prompt")
    assert tpl.variables == ()
    assert tpl.render() == "just a plain prompt"


def test_render_with_mapping_and_kwargs_and_precedence():
    tpl = PromptTemplate("{greeting}, {who}!")
    assert tpl.render({"greeting": "Hello", "who": "world"}) == "Hello, world!"
    # kwargs override the mapping on conflict.
    out = tpl.render({"greeting": "Hi", "who": "there"}, who="you")
    assert out == "Hi, you!"


def test_literal_braces_via_doubling():
    tpl = PromptTemplate("Use {{braces}} and slot {value} here }}{{")
    assert tpl.variables == ("value",)
    assert tpl.render(value="X") == "Use {braces} and slot X here }{"


def test_missing_variable_raises():
    tpl = PromptTemplate("{a} and {b}")
    with pytest.raises(MissingVariablesError, match="b") as exc:
        tpl.render(a="1")
    assert exc.value.missing == ("b",)


def test_unknown_variable_raises_by_default():
    tpl = PromptTemplate("{a}")
    with pytest.raises(UnknownVariablesError, match="typo") as exc:
        tpl.render(a="1", typo="2")
    assert exc.value.unknown == ("typo",)


def test_allow_unknown_ignores_extra_values():
    tpl = PromptTemplate("{a}")
    assert tpl.render({"a": "1", "extra": "ignored"}, allow_unknown=True) == "1"


def test_non_string_values_are_stringified():
    tpl = PromptTemplate("count={n} flag={flag}")
    assert tpl.render(n=42, flag=True) == "count=42 flag=True"


def test_none_value_is_rejected():
    tpl = PromptTemplate("{a}")
    with pytest.raises(TypeError, match="must not be None"):
        tpl.render(a=None)


def test_safe_escaping_strips_control_chars_but_keeps_whitespace():
    tpl = PromptTemplate("<{v}>")
    dirty = "line1\nline2\ttab\x00\x07\x1bkept"
    assert tpl.render(v=dirty) == "<line1\nline2\ttab" + "kept>"


def test_escape_value_helper():
    assert escape_value("clean text") == "clean text"
    assert escape_value("a\x00b\x1fc") == "abc"
    assert escape_value(123) == "123"
    with pytest.raises(TypeError):
        escape_value(None)


def test_braces_in_value_are_not_reinterpreted():
    tpl = PromptTemplate("{a}")
    # A value containing what looks like a slot is emitted verbatim (single pass).
    assert tpl.render(a="{b} literal") == "{b} literal"


@pytest.mark.parametrize(
    "bad",
    [
        "unmatched {open",
        "unmatched close}",
        "empty {}",
        "bad name {1abc}",
        "space {a b}",
        "dotted {a.b}",
    ],
)
def test_malformed_templates_raise_at_construction(bad):
    with pytest.raises(TemplateError):
        PromptTemplate(bad)


def test_non_string_template_raises_type_error():
    with pytest.raises(TypeError, match="template must be a string"):
        PromptTemplate(123)


def test_template_is_hashable_and_frozen():
    tpl = PromptTemplate("{a}")
    assert PromptTemplate("{a}") == tpl
    assert hash(tpl) == hash(PromptTemplate("{a}"))
    with pytest.raises(FrozenInstanceError):
        tpl.template = "changed"  # frozen dataclass


def test_partial_prefills_some_slots():
    tpl = PromptTemplate("[{role}] {question}")
    grounded = tpl.partial(role="assistant")
    assert grounded.variables == ("question",)
    assert grounded.render(question="hi?") == "[assistant] hi?"


def test_partial_rejects_unknown_slot():
    tpl = PromptTemplate("{a}")
    with pytest.raises(UnknownVariablesError):
        tpl.partial(nope="x")


def test_partial_preserves_literal_braces():
    tpl = PromptTemplate("{{keep}} {a} {b}")
    filled = tpl.partial(a="X")
    assert filled.variables == ("b",)
    assert filled.render(b="Y") == "{keep} X Y"


def test_partial_value_with_braces_is_escaped_not_a_new_slot():
    tpl = PromptTemplate("{a} {b}")
    filled = tpl.partial(a="{c}")
    # The injected value must not become a live {c} slot.
    assert filled.variables == ("b",)
    assert filled.render(b="Y") == "{c} Y"


class _EchoModel:
    """Fake async model that echoes the prompt it receives."""

    def __init__(self) -> None:
        self.seen: list[str] = []

    async def generate_content_async(self, prompt: str):
        self.seen.append(prompt)

        class _Resp:
            text = f"echo: {prompt}"

        return _Resp()


async def test_rendered_prompt_feeds_chat_service():
    tpl = PromptTemplate("You are {persona}. Answer: {question}")
    prompt = tpl.render(persona="a concise helper", question="what is 2+2?")
    model = _EchoModel()
    service = ChatService(model)
    reply = await service.generate(prompt)
    assert model.seen[0] == prompt
    assert "what is 2+2?" in reply

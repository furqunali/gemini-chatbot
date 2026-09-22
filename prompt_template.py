"""Prompt-template renderer with named slots, validation and safe escaping.

This module turns a template string containing ``{named}`` slots into a rendered
prompt. It is deliberately provider-neutral and has no dependency on a live API,
mirroring the rest of the chatbot package.

Template syntax
---------------
* ``{name}`` marks a named slot. ``name`` must be a valid Python identifier.
* ``{{`` and ``}}`` are literal ``{`` and ``}`` characters.
* A lone ``{`` or ``}`` (an unmatched or malformed brace) is a template error
  detected when the :class:`PromptTemplate` is constructed, not at render time.

Rendering guarantees
--------------------
* **Required-variable validation** - every slot in the template must be supplied
  at render time; missing slots raise :class:`MissingVariablesError`.
* **Unknown-variable rejection** - by default, supplying a value for a name that
  the template does not declare raises :class:`UnknownVariablesError`. This
  catches typos such as ``{usr}`` vs ``user`` early.
* **Safe escaping** - substituted values are sanitised via :func:`escape_value`,
  which strips ASCII control characters (keeping ``\\t``, ``\\n`` and ``\\r``)
  so a value can never smuggle control bytes into the outgoing prompt. Because
  rendering is single pass, braces inside a value are emitted verbatim and are
  never re-interpreted as slots.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

# Control characters that are safe to keep inside a rendered prompt.
_ALLOWED_CONTROL = frozenset("\t\n\r")


class TemplateError(ValueError):
    """Base error for malformed templates or invalid render arguments."""


class MissingVariablesError(TemplateError):
    """Raised when required slots are not supplied at render time."""

    def __init__(self, missing: tuple[str, ...]) -> None:
        self.missing = missing
        names = ", ".join(missing)
        super().__init__(f"missing required template variable(s): {names}")


class UnknownVariablesError(TemplateError):
    """Raised when values are supplied for slots the template does not declare."""

    def __init__(self, unknown: tuple[str, ...]) -> None:
        self.unknown = unknown
        names = ", ".join(unknown)
        super().__init__(f"unknown template variable(s): {names}")


def escape_value(value: object) -> str:
    """Coerce ``value`` to a safe string for substitution into a prompt.

    ``None`` is rejected because a missing value should surface as a
    :class:`MissingVariablesError`, not silently render as ``"None"``. Every
    other value is converted with :func:`str` and stripped of ASCII control
    characters except tab, newline and carriage return.
    """
    if value is None:
        raise TypeError("template values must not be None")
    text = value if isinstance(value, str) else str(value)
    if not any(_is_stripped_control(ch) for ch in text):
        return text
    return "".join(ch for ch in text if not _is_stripped_control(ch))


def _is_stripped_control(ch: str) -> bool:
    """Return whether ``ch`` is a control character that must be removed."""
    codepoint = ord(ch)
    if ch in _ALLOWED_CONTROL:
        return False
    return codepoint < 0x20 or codepoint == 0x7F


def _parse(template: str) -> tuple[tuple[tuple[str, str], ...], tuple[str, ...]]:
    """Compile ``template`` into segments and the ordered set of slot names.

    Each segment is a ``(kind, value)`` pair where ``kind`` is ``"literal"`` or
    ``"slot"``. Returns the segment tuple and the unique slot names in first-seen
    order. Raises :class:`TemplateError` on malformed braces or bad slot names.
    """
    segments: list[tuple[str, str]] = []
    seen: list[str] = []
    seen_set: set[str] = set()
    buffer: list[str] = []
    i = 0
    length = len(template)

    def flush_literal() -> None:
        if buffer:
            segments.append(("literal", "".join(buffer)))
            buffer.clear()

    while i < length:
        ch = template[i]
        if ch == "{":
            if i + 1 < length and template[i + 1] == "{":
                buffer.append("{")
                i += 2
                continue
            end = template.find("}", i + 1)
            if end == -1:
                raise TemplateError(
                    f"unmatched '{{' at position {i}; use '{{{{' for a literal brace"
                )
            name = template[i + 1 : end]
            if not name:
                raise TemplateError(f"empty slot '{{}}' at position {i}")
            if not name.isidentifier():
                raise TemplateError(
                    f"invalid slot name {name!r}; names must be valid identifiers"
                )
            flush_literal()
            segments.append(("slot", name))
            if name not in seen_set:
                seen_set.add(name)
                seen.append(name)
            i = end + 1
            continue
        if ch == "}":
            if i + 1 < length and template[i + 1] == "}":
                buffer.append("}")
                i += 2
                continue
            raise TemplateError(
                f"unmatched '}}' at position {i}; use '}}}}' for a literal brace"
            )
        buffer.append(ch)
        i += 1

    flush_literal()
    return tuple(segments), tuple(seen)


@dataclass(frozen=True)
class PromptTemplate:
    """A parsed prompt template with named slots and safe rendering.

    The template is compiled once at construction, so malformed braces or invalid
    slot names are reported immediately rather than on first render.
    """

    template: str
    _segments: tuple[tuple[str, str], ...] = field(
        default=(), init=False, repr=False, compare=False
    )
    _variables: tuple[str, ...] = field(
        default=(), init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        if not isinstance(self.template, str):
            raise TypeError("template must be a string")
        segments, variables = _parse(self.template)
        object.__setattr__(self, "_segments", segments)
        object.__setattr__(self, "_variables", variables)

    @property
    def variables(self) -> tuple[str, ...]:
        """Return the required slot names in first-seen order."""
        return self._variables

    def render(
        self,
        values: Mapping[str, object] | None = None,
        *,
        allow_unknown: bool = False,
        **kwargs: object,
    ) -> str:
        """Render the template, substituting each slot with a safe value.

        Values may be passed as a mapping, as keyword arguments, or both;
        keyword arguments take precedence on conflict. Missing required slots
        raise :class:`MissingVariablesError`. Extra values raise
        :class:`UnknownVariablesError` unless ``allow_unknown`` is set.
        """
        merged: dict[str, object] = {}
        if values is not None:
            if not isinstance(values, Mapping):
                raise TypeError("values must be a mapping")
            merged.update(values)
        merged.update(kwargs)

        required = set(self._variables)
        provided = set(merged)

        missing = tuple(name for name in self._variables if name not in provided)
        if missing:
            raise MissingVariablesError(missing)

        if not allow_unknown:
            unknown = tuple(sorted(provided - required))
            if unknown:
                raise UnknownVariablesError(unknown)

        escaped = {name: escape_value(merged[name]) for name in required}
        parts: list[str] = []
        for kind, value in self._segments:
            parts.append(escaped[value] if kind == "slot" else value)
        return "".join(parts)

    def partial(self, **kwargs: object) -> PromptTemplate:
        """Return a new template with some slots pre-filled.

        The supplied values are baked into the template as literal, safely
        escaped text (with braces doubled so they survive re-parsing), leaving
        the remaining slots open. Useful for fixed system preambles.
        """
        unknown = tuple(sorted(set(kwargs) - set(self._variables)))
        if unknown:
            raise UnknownVariablesError(unknown)
        parts: list[str] = []
        for kind, value in self._segments:
            if kind == "literal":
                parts.append(value.replace("{", "{{").replace("}", "}}"))
            elif value in kwargs:
                safe = escape_value(kwargs[value])
                parts.append(safe.replace("{", "{{").replace("}", "}}"))
            else:
                parts.append("{" + value + "}")
        return PromptTemplate("".join(parts))

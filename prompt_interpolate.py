"""Safe ``{var}`` template interpolation that never raises ``KeyError``.

``str.format`` and ``str.format_map`` explode on the first missing key and give
no visibility into which variables were unused. Prompt templates -- where a
missing slot means a broken prompt and an unused variable means a likely typo --
need the opposite: fill what you can, and *report* both the missing and the
unused names so callers can decide what to do.

This module recognises ``{identifier}`` placeholders (Python identifier names).
Literal braces are written doubled -- ``{{`` and ``}}`` -- exactly as in
``str.format``. Anything else, such as ``{ not-an-identifier }``, is left
untouched as literal text so malformed markup can never crash interpolation.

The interpolation is pure and deterministic; ``missing`` and ``unused`` are
returned sorted so results are stable across runs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping

_TOKEN = re.compile(r"\{\{|\}\}|\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass(frozen=True)
class InterpolationResult:
    """Immutable outcome of an interpolation pass."""

    text: str
    missing: tuple[str, ...]
    unused: tuple[str, ...]


def find_variables(template: str) -> tuple[str, ...]:
    """Return the distinct placeholder names in ``template``, sorted."""
    if not isinstance(template, str):
        raise TypeError("template must be a string")
    names = {match.group(1) for match in _TOKEN.finditer(template) if match.group(1)}
    return tuple(sorted(names))


def interpolate(
    template: str,
    variables: Mapping[str, object],
    strict: bool = False,
    default: str = "",
) -> InterpolationResult:
    """Interpolate ``variables`` into ``template`` without ever raising KeyError.

    Placeholders present in ``variables`` are replaced by ``str(value)``.
    Placeholders with no matching variable are replaced by ``default`` and
    reported in ``missing``. Variables never referenced by the template are
    reported in ``unused``.

    When ``strict`` is true a :class:`ValueError` is raised if any placeholder is
    missing, after the full set of missing names has been collected so the error
    message is complete.
    """
    if not isinstance(template, str):
        raise TypeError("template must be a string")
    if not isinstance(variables, Mapping):
        raise TypeError("variables must be a mapping")
    if not isinstance(default, str):
        raise TypeError("default must be a string")
    for key in variables:
        if not isinstance(key, str):
            raise TypeError("variable keys must be strings")

    referenced: set[str] = set()
    missing: set[str] = set()

    def _replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if token == "{{":
            return "{"
        if token == "}}":
            return "}"
        name = match.group(1)
        referenced.add(name)
        if name in variables:
            return str(variables[name])
        missing.add(name)
        return default

    text = _TOKEN.sub(_replace, template)

    if strict and missing:
        raise ValueError(
            "missing variables: " + ", ".join(sorted(missing))
        )

    unused = set(variables) - referenced
    return InterpolationResult(
        text=text,
        missing=tuple(sorted(missing)),
        unused=tuple(sorted(unused)),
    )

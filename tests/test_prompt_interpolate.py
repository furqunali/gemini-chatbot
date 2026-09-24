import pytest

from prompt_interpolate import (
    InterpolationResult,
    find_variables,
    interpolate,
)


def test_basic_substitution():
    result = interpolate("Hello {name}!", {"name": "Ada"})
    assert result.text == "Hello Ada!"
    assert result.missing == ()
    assert result.unused == ()


def test_returns_result_record():
    result = interpolate("{a}", {"a": 1})
    assert isinstance(result, InterpolationResult)


def test_non_string_values_are_stringified():
    result = interpolate("count={n}", {"n": 42})
    assert result.text == "count=42"


def test_missing_variable_reported_not_raised():
    result = interpolate("Hi {name}, {greeting}", {"name": "Ada"})
    assert result.text == "Hi Ada, "
    assert result.missing == ("greeting",)


def test_missing_uses_default():
    result = interpolate("Hi {name}", {}, default="[?]")
    assert result.text == "Hi [?]"
    assert result.missing == ("name",)


def test_unused_variables_reported():
    result = interpolate("Hi {name}", {"name": "Ada", "extra": "x", "other": "y"})
    assert result.unused == ("extra", "other")


def test_missing_and_unused_are_sorted():
    result = interpolate("{b} {a}", {"z": 1, "a": 2})
    assert result.missing == ("b",)
    assert result.unused == ("z",)


def test_escaped_braces_are_literal():
    result = interpolate("{{not a var}} {x}", {"x": "X"})
    assert result.text == "{not a var} X"
    assert result.missing == ()


def test_repeated_placeholder():
    result = interpolate("{x}-{x}", {"x": "9"})
    assert result.text == "9-9"


def test_malformed_placeholder_left_literal():
    # Space inside the braces means it is not a valid identifier placeholder.
    result = interpolate("{ not valid }", {})
    assert result.text == "{ not valid }"
    assert result.missing == ()


def test_strict_raises_on_missing():
    with pytest.raises(ValueError, match="missing variables: a, b"):
        interpolate("{a}{b}", {}, strict=True)


def test_strict_ok_when_all_present():
    result = interpolate("{a}", {"a": "ok"}, strict=True)
    assert result.text == "ok"


def test_find_variables_distinct_and_sorted():
    assert find_variables("{b} {a} {b} literal {{c}}") == ("a", "b")


def test_template_type_validation():
    with pytest.raises(TypeError, match="template must be a string"):
        interpolate(123, {})  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="template must be a string"):
        find_variables(123)  # type: ignore[arg-type]


def test_variables_mapping_validation():
    with pytest.raises(TypeError, match="variables must be a mapping"):
        interpolate("{x}", ["x"])  # type: ignore[arg-type]


def test_variable_keys_must_be_strings():
    with pytest.raises(TypeError, match="variable keys must be strings"):
        interpolate("{x}", {1: "a"})  # type: ignore[dict-item]


def test_default_must_be_string():
    with pytest.raises(TypeError, match="default must be a string"):
        interpolate("{x}", {}, default=0)  # type: ignore[arg-type]

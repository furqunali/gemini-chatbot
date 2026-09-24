import pytest

from token_estimator import (
    TokenEstimate,
    estimate,
    estimate_messages_tokens,
    estimate_tokens,
)


def test_char_based_matches_existing_convention():
    # 8 chars / 4 chars-per-token == 2, one word * 1.3 == 2 -> max 2.
    assert estimate_tokens("a" * 8) == 2


def test_word_signal_dominates_for_many_short_words():
    text = "a b c d e f g h"  # 15 chars, 8 words
    # char estimate ceil(15/4)=4; word estimate ceil(8*1.3)=11 -> 11.
    assert estimate_tokens(text) == 11


def test_char_signal_dominates_for_one_long_word():
    text = "supercalifragilistic"  # 20 chars, 1 word
    # char ceil(20/4)=5; word ceil(1*1.3)=2 -> 5.
    assert estimate_tokens(text) == 5


def test_empty_string_is_zero_tokens():
    assert estimate_tokens("") == 0


def test_whitespace_only_has_no_words_but_counts_chars():
    est = estimate("    ")  # 4 chars, 0 words
    assert est.words == 0
    assert est.estimated_tokens == 1  # ceil(4/4)


def test_estimate_returns_breakdown_record():
    est = estimate("hello world")
    assert isinstance(est, TokenEstimate)
    assert est.characters == 11
    assert est.words == 2


def test_estimate_record_is_frozen():
    est = estimate("hi")
    with pytest.raises(AttributeError):
        est.estimated_tokens = 99  # type: ignore[misc]


def test_custom_ratios_change_result():
    # chars_per_token=1 => char estimate == length.
    assert estimate_tokens("abcd", chars_per_token=1.0) == 4


def test_messages_sum_content_plus_overhead():
    messages = [
        {"role": "user", "content": "a" * 8},   # 2 tokens (char signal)
        {"role": "assistant", "content": "b" * 4},  # 2 tokens (word signal wins)
    ]
    # overhead=0 -> 2 + 2
    assert estimate_messages_tokens(messages, per_message_overhead=0) == 4
    # default overhead=3 per message -> 4 + 3*2
    assert estimate_messages_tokens(messages) == 10


def test_messages_empty_list_is_zero():
    assert estimate_messages_tokens([]) == 0


def test_text_type_validation():
    with pytest.raises(TypeError, match="text must be a string"):
        estimate_tokens(123)  # type: ignore[arg-type]


def test_ratio_validation():
    with pytest.raises(ValueError, match="chars_per_token must be positive"):
        estimate_tokens("hi", chars_per_token=0)
    with pytest.raises(ValueError, match="tokens_per_word must be positive"):
        estimate_tokens("hi", tokens_per_word=-1)


def test_messages_structure_validation():
    with pytest.raises(TypeError, match="messages must be a list"):
        estimate_messages_tokens("not a list")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"messages\[0\] must be a dict"):
        estimate_messages_tokens(["nope"])  # type: ignore[list-item]
    with pytest.raises(ValueError, match="must have a 'content' key"):
        estimate_messages_tokens([{"role": "user"}])
    with pytest.raises(TypeError, match="content'\\] must be a string"):
        estimate_messages_tokens([{"role": "user", "content": 5}])  # type: ignore[dict-item]


def test_overhead_validation():
    with pytest.raises(TypeError, match="per_message_overhead must be an int"):
        estimate_messages_tokens([], per_message_overhead=True)
    with pytest.raises(ValueError, match="per_message_overhead must not be negative"):
        estimate_messages_tokens([], per_message_overhead=-1)

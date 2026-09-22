import asyncio

import pytest

from stream_aggregator import (
    AggregatedResponse,
    StreamAggregationError,
    StreamUsage,
    aggregate_stream,
)


async def _agen(items):
    for item in items:
        yield item


class _Chunk:
    def __init__(self, text):
        self.text = text


async def test_joins_string_chunks_and_strips_result():
    result = await aggregate_stream(_agen(["  Hello", ", ", "world  "]))
    assert isinstance(result, AggregatedResponse)
    assert result.text == "Hello, world"
    assert result.truncated is False
    assert result.usage.chunk_count == 3
    assert result.usage.content_chunks == 3
    assert result.usage.empty_chunks == 0
    assert result.usage.char_count == len("Hello, world")


async def test_joins_objects_exposing_text_attribute():
    result = await aggregate_stream(_agen([_Chunk("a"), _Chunk("b"), _Chunk("c")]))
    assert result.text == "abc"


async def test_separator_only_between_content_chunks():
    result = await aggregate_stream(_agen(["a", "", "b"]), separator="-")
    # The empty chunk is skipped so no doubled separator appears.
    assert result.text == "a-b"
    assert result.usage.empty_chunks == 1
    assert result.usage.content_chunks == 2
    assert result.usage.chunk_count == 3


async def test_none_text_counts_as_empty_chunk():
    result = await aggregate_stream(_agen([_Chunk("x"), _Chunk(None), "y"]))
    assert result.text == "xy"
    assert result.usage.empty_chunks == 1
    assert result.usage.content_chunks == 2


async def test_empty_stream_returns_blank_response():
    result = await aggregate_stream(_agen([]))
    assert result.text == ""
    assert result.usage == StreamUsage()


async def test_max_chars_truncates_and_flags():
    result = await aggregate_stream(_agen(["12345", "67890"]), max_chars=7)
    assert result.text == "1234567"
    assert result.truncated is True
    assert result.usage.char_count == 7
    # Second chunk was partially consumed, so it still counts as content.
    assert result.usage.content_chunks == 2


async def test_max_chars_boundary_is_not_truncated():
    result = await aggregate_stream(_agen(["1234", "5678"]), max_chars=8)
    assert result.text == "12345678"
    assert result.truncated is False


async def test_truncation_closes_underlying_stream_early():
    closed = {"value": False}
    consumed = []

    async def gen():
        try:
            for item in ["aaaa", "bbbb", "cccc"]:
                consumed.append(item)
                yield item
        finally:
            closed["value"] = True

    result = await aggregate_stream(gen(), max_chars=5)
    assert result.text == "aaaab"
    assert result.truncated is True
    # The third chunk must never be produced once the budget is hit.
    assert "cccc" not in consumed
    assert closed["value"] is True


async def test_cancellation_closes_underlying_stream():
    closed = {"value": False}
    started = asyncio.Event()

    async def gen():
        try:
            started.set()
            yield "partial"
            await asyncio.sleep(3600)
            yield "never"
        finally:
            closed["value"] = True

    task = asyncio.ensure_future(aggregate_stream(gen()))
    await started.wait()
    await asyncio.sleep(0.05)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert closed["value"] is True


async def test_invalid_text_type_raises_aggregation_error():
    with pytest.raises(StreamAggregationError):
        await aggregate_stream(_agen([_Chunk(123)]))


async def test_chunk_without_text_attribute_raises():
    with pytest.raises(StreamAggregationError):
        await aggregate_stream(_agen([object()]))


async def test_non_async_iterable_rejected():
    with pytest.raises(TypeError):
        await aggregate_stream(["not", "async"])


async def test_separator_must_be_string():
    with pytest.raises(TypeError):
        await aggregate_stream(_agen(["a"]), separator=1)


@pytest.mark.parametrize("bad", [0, -1, True, 3.5])
async def test_invalid_max_chars_rejected(bad):
    with pytest.raises((ValueError, TypeError)):
        await aggregate_stream(_agen(["a"]), max_chars=bad)


def test_usage_and_response_as_dict_shapes():
    usage = StreamUsage(chunk_count=2, content_chunks=1, empty_chunks=1, char_count=3)
    assert usage.as_dict() == {
        "chunk_count": 2,
        "content_chunks": 1,
        "empty_chunks": 1,
        "char_count": 3,
    }
    response = AggregatedResponse(text="abc", usage=usage, truncated=True)
    assert response.as_dict() == {
        "text": "abc",
        "truncated": True,
        "usage": usage.as_dict(),
    }

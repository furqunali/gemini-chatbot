"""Aggregate async streaming chunks into a single chatbot message.

Gemini's async streaming API yields many small chunk objects rather than one
response.  This module joins such an ``AsyncIterable`` into a final message
while recording usage statistics (how many chunks arrived, how many were empty,
how long the joined text is) and guaranteeing that the underlying stream is
always closed -- even when the consuming task is cancelled or an optional
character budget is reached.

The aggregator is provider-independent: a chunk may be a plain ``str`` or any
object exposing a ``.text`` attribute (the shape used by the Gemini SDK and by
the fakes in ``tests/``).
"""

from __future__ import annotations

from collections.abc import AsyncIterable
from dataclasses import dataclass
from typing import Any

from chatbot_errors import ChatbotError


class StreamAggregationError(ChatbotError):
    """Raised when a streamed chunk cannot be interpreted as text."""


@dataclass(frozen=True)
class StreamUsage:
    """Usage statistics gathered while consuming a response stream."""

    chunk_count: int = 0
    content_chunks: int = 0
    empty_chunks: int = 0
    char_count: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "chunk_count": self.chunk_count,
            "content_chunks": self.content_chunks,
            "empty_chunks": self.empty_chunks,
            "char_count": self.char_count,
        }


@dataclass(frozen=True)
class AggregatedResponse:
    """The joined message plus usage statistics for a consumed stream."""

    text: str
    usage: StreamUsage
    truncated: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "truncated": self.truncated,
            "usage": self.usage.as_dict(),
        }


def _chunk_text(chunk: Any) -> str:
    """Extract text from a chunk without assuming a concrete provider type.

    A ``str`` chunk is returned unchanged.  Otherwise the chunk must expose a
    ``.text`` attribute that is either ``None`` (treated as an empty chunk) or a
    ``str``.  Anything else is a programming/provider error and is rejected.
    """
    if isinstance(chunk, str):
        return chunk
    if not hasattr(chunk, "text"):
        raise StreamAggregationError(
            "stream chunk must be a string or expose a 'text' attribute"
        )
    text = chunk.text
    if text is None:
        return ""
    if not isinstance(text, str):
        raise StreamAggregationError("stream chunk 'text' must be a string or None")
    return text


async def aggregate_stream(
    chunks: AsyncIterable[Any],
    *,
    separator: str = "",
    max_chars: int | None = None,
) -> AggregatedResponse:
    """Join an async iterable of chunks into a single :class:`AggregatedResponse`.

    Args:
        chunks: An async iterable whose items are strings or objects with a
            ``.text`` attribute.
        separator: Inserted between non-empty chunk texts when joining.
        max_chars: Optional upper bound on the number of content characters to
            collect (separators excluded).  When the budget is reached the
            final chunk is trimmed, the stream is closed early, and
            ``truncated`` is set on the result.

    Returns:
        An :class:`AggregatedResponse` with the joined, whitespace-stripped text
        and a :class:`StreamUsage` breakdown.

    Raises:
        TypeError: If ``chunks`` is not an async iterable or ``separator`` is
            not a string, or ``max_chars`` is not an int.
        ValueError: If ``max_chars`` is not positive.
        StreamAggregationError: If a chunk cannot be interpreted as text.

    The underlying stream's ``aclose`` (if present) is always awaited before
    returning or propagating, so cancellation never leaks an open async
    generator.
    """
    if not isinstance(separator, str):
        raise TypeError("separator must be a string")
    if max_chars is not None:
        if isinstance(max_chars, bool) or not isinstance(max_chars, int):
            raise TypeError("max_chars must be an int or None")
        if max_chars <= 0:
            raise ValueError("max_chars must be positive")
    aiter_method = getattr(chunks, "__aiter__", None)
    if not callable(aiter_method):
        raise TypeError("chunks must be an async iterable")

    iterator = aiter_method()
    parts: list[str] = []
    chunk_count = 0
    content_chunks = 0
    empty_chunks = 0
    content_len = 0
    truncated = False

    try:
        async for chunk in iterator:
            chunk_count += 1
            piece = _chunk_text(chunk)
            if not piece:
                empty_chunks += 1
                continue
            if max_chars is not None and content_len + len(piece) > max_chars:
                piece = piece[: max_chars - content_len]
                truncated = True
            if piece:
                parts.append(piece)
                content_chunks += 1
                content_len += len(piece)
            if truncated:
                break
    finally:
        aclose = getattr(iterator, "aclose", None)
        if callable(aclose):
            await aclose()

    text = separator.join(parts).strip()
    usage = StreamUsage(
        chunk_count=chunk_count,
        content_chunks=content_chunks,
        empty_chunks=empty_chunks,
        char_count=len(text),
    )
    return AggregatedResponse(text=text, usage=usage, truncated=truncated)

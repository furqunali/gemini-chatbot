"""Gemini chatbot API and backwards-compatible CLI entry point."""
from __future__ import annotations

import asyncio

from dotenv import load_dotenv

from chatbot_config import get_api_key, get_model_name
from chatbot_service import ChatService
from gemini_provider import build_model

load_dotenv()

class ChatBot:
    """Small async wrapper around the Gemini text-generation API."""
    def __init__(self, api_key=None, model_name=None):
        api_key = api_key or get_api_key()
        selected_model = get_model_name(model_name)
        self.model = build_model(api_key, selected_model)
        self._service = ChatService(self.model)

    async def chat(self, prompt):
        """Generate a response for a single user prompt."""
        service = getattr(self, "_service", ChatService(self.model))
        try:
            return await service.generate(prompt)
        except Exception as exc:  # noqa: BLE001 - never leak a raw traceback to the caller
            return f"Bot Error: {exc}"

async def main():
    from cli import run_cli
    try:
        bot = ChatBot()
    except Exception as exc:  # noqa: BLE001 - top-level guard surfaces any startup failure to the user
        print(f"Gemini Bot: startup error: {exc}")
        return
    await run_cli(bot)

if __name__ == "__main__":
    asyncio.run(main())

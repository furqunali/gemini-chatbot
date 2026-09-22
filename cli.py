"""Command-line entry point for the async Gemini chatbot."""
from __future__ import annotations

import argparse
import asyncio

from chatbot_config import get_api_key, get_model_name
from chatbot_service import ChatService
from chatbot_validation import is_exit_command, validate_prompt
from gemini_provider import build_model


def build_parser():
    p = argparse.ArgumentParser(description="Chat with Gemini from a terminal")
    p.add_argument("--prompt")
    p.add_argument("--model")
    return p


def build_service(model_name):
    """Build a chatbot service; provider construction is synchronous."""
    return ChatService(build_model(get_api_key(), model_name))


async def run_once(prompt, model_name):
    return await build_service(model_name).generate(prompt)


async def interactive(model_name):
    service = build_service(model_name)
    print(f"Gemini CLI ({model_name}). Type 'exit' or 'quit' to stop.")
    while True:
        try:
            raw = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        prompt = validate_prompt(raw)
        if is_exit_command(prompt):
            return 0
        if not prompt:
            print("Please enter a message.")
            continue
        print(await service.generate(prompt))


def main():
    a = build_parser().parse_args()
    model = get_model_name(a.model)
    if a.prompt is not None:
        prompt = validate_prompt(a.prompt)
        if not prompt:
            print("Please enter a message.")
            return 0
        print(asyncio.run(run_once(prompt, model)))
        return 0
    return asyncio.run(interactive(model))


if __name__ == "__main__":
    raise SystemExit(main())


async def run_cli(bot=None):
    """Backward-compatible interactive loop used by the legacy entry point."""
    if bot is None:
        from projects12 import ChatBot

        try:
            bot = ChatBot()
        except Exception as exc:  # noqa: BLE001 - top-level guard surfaces any startup failure to the user
            print(f"Gemini Bot: startup error: {exc}")
            return
    print("Gemini Bot: Hello! Type 'quit' to exit.\\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\\nGemini Bot: Goodbye!")
            return
        if user_input.lower() in {"quit", "exit"}:
            print("Gemini Bot: Goodbye!")
            return
        try:
            response = await bot.chat(user_input)
        except Exception as exc:  # noqa: BLE001 - chat loop must not crash on any provider error
            response = f"Bot Error: {exc}"
        print(f"Bot: {response}\\n")

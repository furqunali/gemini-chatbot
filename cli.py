"""Interactive command-line loop for the Gemini chatbot."""
from __future__ import annotations
import asyncio
from projects12 import ChatBot

EXIT_COMMANDS = {"quit", "exit"}

async def run_cli(bot: ChatBot | None = None) -> None:
    """Run the interactive loop with clean terminal shutdown handling."""
    try:
        bot = bot or ChatBot()
    except Exception as exc:
        print(f"Gemini Bot: startup error: {exc}")
        return
    print("Gemini Bot: Hello! Type 'quit' to exit.\\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\\nGemini Bot: Goodbye!")
            return
        if user_input.lower() in EXIT_COMMANDS:
            print("Gemini Bot: Goodbye!")
            return
        try:
            response = await bot.chat(user_input)
        except Exception as exc:
            response = f"Bot Error: {exc}"
        print(f"Bot: {response}\\n")


def main() -> None:
    asyncio.run(run_cli())

import os
import asyncio

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


class ChatBot:
    """Small async wrapper around the Gemini text-generation API."""

    def __init__(self, api_key=None, model_name=None):
        api_key = api_key or GEMINI_API_KEY
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. Add it to the environment or .env file."
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name or GEMINI_MODEL)

    async def chat(self, prompt):
        """Generate a response for a single user prompt."""
        prompt = prompt.strip()
        if not prompt:
            return "Please enter a message."

        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as exc:
            return f"Bot Error: {exc}"


async def main():
    bot = ChatBot()
    print("Gemini Bot: Hello! Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break

        response = await bot.chat(user_input)
        print(f"Bot: {response}\n")


if __name__ == "__main__":
    asyncio.run(main())

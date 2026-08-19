import os
import google.generativeai as genai
import asyncio
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # set in a .env file (see .env.example)

class ChatBot:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.0-pro')  # ✅ Correct model
    
    async def chat(self, prompt):
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            return f"Bot Error: {str(e)}"  # Better error reporting

async def main():
    bot = ChatBot()
    print("Gemini Bot: Hello! Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ('quit', 'exit'):
            break
        
        response = await bot.chat(user_input)
        print(f"Bot: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())
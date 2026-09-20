"""Command-line entry point for the async Gemini chatbot."""
from __future__ import annotations
import argparse, asyncio
from chatbot_config import get_model_name
from chatbot_service import ChatService
from chatbot_validation import is_exit_command, validate_prompt
from chatbot_config import get_api_key

def build_parser():
    p=argparse.ArgumentParser(description="Chat with Gemini from a terminal")
    p.add_argument("--prompt"); p.add_argument("--model")
    return p

async def build_service(model_name):
    import google.generativeai as genai
    genai.configure(api_key=get_api_key())
    return ChatService(genai.GenerativeModel(model_name))

async def run_once(prompt, model_name):
    return await (await build_service(model_name)).generate(prompt)

async def interactive(model_name):
    service=await build_service(model_name)
    print(f"Gemini CLI ({model_name}). Type 'exit' or 'quit' to stop.")
    while True:
        try: raw=input("> ")
        except (EOFError,KeyboardInterrupt): print(); return 0
        prompt=validate_prompt(raw)
        if is_exit_command(prompt): return 0
        if not prompt: print("Please enter a message."); continue
        print(await service.generate(prompt))

def main():
    a=build_parser().parse_args(); model=get_model_name(a.model)
    if a.prompt is not None:
        prompt=validate_prompt(a.prompt)
        if not prompt: print("Please enter a message."); return 0
        print(asyncio.run(run_once(prompt,model))); return 0
    return asyncio.run(interactive(model))

if __name__=="__main__":
    raise SystemExit(main())

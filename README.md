# 🤖 Gemini AI Chatbot (Async)

An asynchronous Python chatbot built around Google's Generative AI API.

## Features

- Async Gemini responses using `async`/`await`
- API key loaded from `GEMINI_API_KEY`
- Configurable model through `GEMINI_MODEL`
- Clear validation for missing credentials and empty prompts
- Basic automated tests for input validation

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.8-flash
```

Run the chatbot:

```bash
python projects12.py
```

Run tests:

```bash
pip install pytest
pytest
```

Never commit a real API key. Use `.env.example` as the template for local configuration.



## Reliability

Provider failures are classified through a shared retry policy. Transient HTTP-style status codes, including deeply wrapped provider errors, can be retried with bounded backoff, while non-retryable failures are surfaced without unnecessary retries. Retry-policy parameters are validated before use.

---

*Part of [Furqan Ali](https://github.com/furqunali)'s portfolio — AI & Intelligent Automation / Digital Transformation.*

import anthropic
import json
import os
from functools import lru_cache


@lru_cache(maxsize=1)
def _client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Check backend/.env.")
    return anthropic.Anthropic(api_key=api_key)

SYSTEM_PROMPT = """You are a contact form classifier for a business website.

Classify the incoming message into exactly ONE of these categories:
- sales: interested in buying, pricing questions, demo requests, product inquiries
- support: existing customer with a problem, bug report, help request, account issue
- partnership: collaboration proposals, affiliate requests, integration inquiries, B2B
- spam: irrelevant, promotional, bot-generated, or malicious content

Respond ONLY with a JSON object in this exact format, no other text:
{
  "category": "sales|support|partnership|spam",
  "confidence": "high|medium|low",
  "reasoning": "one sentence explanation"
}"""


def classify_message(name: str, email: str, message: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Name: {name}\nEmail: {email}\nMessage: {message}"
        }]
    )
    raw_text = response.content[0].text.strip()
    return json.loads(raw_text)

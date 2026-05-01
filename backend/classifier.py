import anthropic
import json
import logging
import os
from functools import lru_cache

logger = logging.getLogger(__name__)

SALES_KEYWORDS = ("buy", "price", "pricing", "quote", "demo", "trial", "purchase", "cost", "sales", "subscription")
SUPPORT_KEYWORDS = ("bug", "issue", "error", "broken", "help", "not working", "problem", "fix", "support", "account")
PARTNERSHIP_KEYWORDS = ("partner", "partnership", "collaborat", "integrat", "affiliate", "b2b", "reseller")
SPAM_KEYWORDS = ("seo services", "rank #1", "click here", "crypto", "investment opportunity", "viagra", "lottery")


def _mock_enabled() -> bool:
    return os.getenv("MOCK_CLASSIFIER", "").strip().lower() in ("1", "true", "yes")


def _mock_classify(message: str) -> dict:
    text = message.lower()

    def hits(keywords: tuple[str, ...]) -> int:
        return sum(1 for kw in keywords if kw in text)

    scores = {
        "spam": hits(SPAM_KEYWORDS),
        "partnership": hits(PARTNERSHIP_KEYWORDS),
        "support": hits(SUPPORT_KEYWORDS),
        "sales": hits(SALES_KEYWORDS),
    }
    category, score = max(scores.items(), key=lambda kv: kv[1])

    if score == 0:
        return {
            "category": "sales",
            "confidence": "low",
            "reasoning": "Mock classifier: no keywords matched, defaulted to sales.",
        }

    confidence = "high" if score >= 2 else "medium"
    return {
        "category": category,
        "confidence": confidence,
        "reasoning": f"Mock classifier: matched {score} '{category}' keyword(s).",
    }


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
    if _mock_enabled():
        logger.info("MOCK_CLASSIFIER enabled — skipping Anthropic API call.")
        return _mock_classify(message)

    try:
        response = _client().messages.create(
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
    except (anthropic.APIError, anthropic.APIConnectionError, json.JSONDecodeError) as exc:
        # Graceful degradation: if the API is unavailable (credits, network, parse error),
        # fall back to the keyword classifier so the demo keeps working.
        logger.warning("Anthropic API unavailable (%s) — falling back to mock classifier.", exc)
        return _mock_classify(message)

import logging
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from classifier import classify_message
from models import ClassifyResponse, ContactRequest
from slack import channel_for, post_to_slack

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Contact Form Router", version="1.0.0")

_default_origins = "http://localhost:5173"
_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/classify", response_model=ClassifyResponse)
def classify(payload: ContactRequest) -> ClassifyResponse:
    try:
        result = classify_message(payload.name, payload.email, payload.message)
    except Exception as exc:
        logger.exception("Classification failed")
        raise HTTPException(status_code=502, detail=f"Classification failed: {exc}")

    category = result.get("category", "sales")
    confidence = result.get("confidence", "low")
    reasoning = result.get("reasoning", "")

    slack_posted = post_to_slack(
        category=category,
        name=payload.name,
        email=payload.email,
        message=payload.message,
        reasoning=reasoning,
    )

    return ClassifyResponse(
        category=category,
        confidence=confidence,
        reasoning=reasoning,
        slack_posted=slack_posted,
        routed_to=channel_for(category),
    )

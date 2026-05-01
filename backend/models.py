from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=1, max_length=5000)


class ClassifyResponse(BaseModel):
    category: Literal["sales", "support", "partnership", "spam"]
    confidence: Literal["high", "medium", "low"]
    reasoning: str
    slack_posted: bool
    routed_to: str

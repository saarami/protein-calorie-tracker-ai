from __future__ import annotations

import json
import logging

from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.openai.client import get_openai_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a nutrition estimator.
Return ONLY valid JSON (no markdown, no extra text).
The JSON schema MUST be:
{
  "title": "1-2 words short title in the same language as the input",
  "totals": { "calories": number, "protein_g": number },
  "items": [
    { "name": string, "quantity": number|null, "unit": string|null, "calories": number, "protein_g": number }
  ],
  "notes": [string]
}
Rules:
- If unsure, estimate conservatively and add a note in notes.
- calories and protein_g must be >= 0.
- Keep title short (1-2 words).
"""


class ParsedItem(BaseModel):
    name: str
    quantity: float | None = None
    unit: str | None = None
    calories: int = Field(ge=0)
    protein_g: float = Field(ge=0)


class ParsedTotals(BaseModel):
    calories: int = Field(ge=0)
    protein_g: float = Field(ge=0)


class ParsedMeal(BaseModel):
    title: str
    totals: ParsedTotals
    items: list[ParsedItem]
    notes: list[str] = Field(default_factory=list)


def _extract_json(text: str) -> str:
    # Best-effort: find first JSON object
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return text
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def parse_meal(text: str) -> ParsedMeal:
    client = get_openai_client()

    def call(prompt: str) -> str:
        # Use Chat Completions API (compatible with openai==1.55.3)
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""

    raw = call(text)
    raw_json = _extract_json(raw)

    try:
        data = json.loads(raw_json)
        return ParsedMeal.model_validate(data)
    except Exception:
        # retry once for invalid JSON
        fix_prompt = f"Fix this to be ONLY valid JSON that matches the schema exactly.\n\n{raw}"
        raw2 = call(fix_prompt)
        raw2_json = _extract_json(raw2)
        try:
            data2 = json.loads(raw2_json)
            return ParsedMeal.model_validate(data2)
        except Exception:
            logger.exception("Failed to parse OpenAI output as JSON")
            raise

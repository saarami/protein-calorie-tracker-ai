from __future__ import annotations

from openai import OpenAI

from app.core.config import settings


def get_openai_client() -> OpenAI:
    if not settings.openai_api_key or settings.openai_api_key == "change_me":
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return OpenAI(api_key=settings.openai_api_key)

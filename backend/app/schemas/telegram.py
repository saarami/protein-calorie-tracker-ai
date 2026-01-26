from __future__ import annotations

from pydantic import BaseModel


class LinkCodeResponse(BaseModel):
    code: str
    expires_in: int


class TelegramStatusResponse(BaseModel):
    is_linked: bool
    linked_at: str | None = None
    chat_id_masked: str | None = None

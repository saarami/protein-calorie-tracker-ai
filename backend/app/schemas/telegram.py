from __future__ import annotations

from typing import Optional, Literal

from pydantic import BaseModel



class LinkCodeResponse(BaseModel):
    code: str
    expires_in: int


class TelegramStatusResponse(BaseModel):
    is_linked: bool
    linked_at: str | None = None
    chat_id_masked: str | None = None


class TgChat(BaseModel):
    id: int
    type: Literal["private", "group", "supergroup", "channel"] | str


class TgMessage(BaseModel):
    chat: TgChat
    text: Optional[str] = None


class TgUpdate(BaseModel):
    message: Optional[TgMessage] = None
    edited_message: Optional[TgMessage] = None

    def pick_message(self) -> Optional[TgMessage]:
        """
        Telegram may send either `message` or `edited_message`.
        We only care about text messages.
        """
        return self.message or self.edited_message

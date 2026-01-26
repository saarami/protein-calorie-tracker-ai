from __future__ import annotations

import datetime
import uuid

from sqlalchemy.orm import Session

from app.models.telegram_link import TelegramLink
from app.models.telegram_link_code import TelegramLinkCode


class TelegramRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_link_by_user(self, user_id: uuid.UUID) -> TelegramLink | None:
        return (
            self.db.query(TelegramLink)
            .filter(TelegramLink.user_id == user_id)
            .one_or_none()
        )

    def get_link_by_chat(self, chat_id: int) -> TelegramLink | None:
        return (
            self.db.query(TelegramLink)
            .filter(TelegramLink.chat_id == chat_id)
            .one_or_none()
        )

    def create_link(self, *, user_id: uuid.UUID, chat_id: int) -> TelegramLink:
        link = TelegramLink(user_id=user_id, chat_id=chat_id)
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def create_link_code(
        self,
        *,
        user_id: uuid.UUID,
        code_hash: str,
        expires_at: datetime.datetime,
    ) -> TelegramLinkCode:
        row = TelegramLinkCode(
            user_id=user_id,
            code_hash=code_hash,
            expires_at=expires_at,
            used_at=None,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_code(self, code_hash: str) -> TelegramLinkCode | None:
        return (
            self.db.query(TelegramLinkCode)
            .filter(TelegramLinkCode.code_hash == code_hash)
            .one_or_none()
        )

    def mark_code_used(self, row: TelegramLinkCode) -> None:
        row.used_at = datetime.datetime.now(datetime.timezone.utc)
        self.db.commit()

from __future__ import annotations

import datetime
import hashlib
import hmac
import logging
import random
import string
from zoneinfo import ZoneInfo

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import http_error, ErrorCodes
from app.repositories.telegram_repository import TelegramRepository
from app.repositories.user_repository import UserRepository
from app.repositories.meal_repository import MealRepository
from app.services.meals.meal_service import MealService
from app.services.telegram.messages import meal_added_message, today_summary_message

logger = logging.getLogger(__name__)

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # avoid O/0/I/1


def _hash_code(code: str) -> str:
    if not settings.telegram_webhook_secret or settings.telegram_webhook_secret == "change_me":
        # still hash deterministically in dev
        salt = "dev_salt"
    else:
        salt = settings.telegram_webhook_secret
    digest = hashlib.sha256((salt + ":" + code).encode("utf-8")).hexdigest()
    return digest


def generate_code(length: int = 6) -> str:
    return "".join(random.choice(ALPHABET) for _ in range(length))


async def send_telegram_message(chat_id: int, text: str) -> None:
    if not settings.telegram_bot_token or settings.telegram_bot_token == "change_me":
        logger.warning("TELEGRAM_BOT_TOKEN not configured; skipping send_message")
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()


class TelegramService:
    def __init__(self, db: Session):
        self.repo = TelegramRepository(db)
        self.meal_repo = MealRepository(db)
        self.meal_service = MealService(db)


    def create_link_code(self, user_id):
        # block if already linked
        if self.repo.get_link_by_user(user_id):
            raise http_error(409, ErrorCodes.TELEGRAM_ALREADY_LINKED, "Already linked")
        code = generate_code(6)
        code_hash = _hash_code(code)
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
        self.repo.create_link_code(user_id=user_id, code_hash=code_hash, expires_at=expires_at)
        return code

    def status(self, user_id):
        link = self.repo.get_link_by_user(user_id)
        if not link:
            return {"is_linked": False, "linked_at": None, "chat_id_masked": None}
        s = str(link.chat_id)
        masked = "*" * max(0, len(s) - 4) + s[-4:]
        return {"is_linked": True, "linked_at": link.linked_at.isoformat(), "chat_id_masked": masked}

    async def handle_update(self, update: dict) -> None:
        message = update.get("message") or update.get("edited_message")
        if not message:
            return
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is None:
            return
        text = (message.get("text") or "").strip()
        if not text:
            return

        # only private chat (as per spec)
        if chat.get("type") != "private":
            return

        if text.startswith("/start"):
            await send_telegram_message(chat_id, "Send /link <code> to connect, then send meal text.")
            return

        if text.startswith("/today"):
            link = self.repo.get_link_by_chat(chat_id)
            if not link:
                await send_telegram_message(chat_id, "Not linked. Use /link <code> from the app.")
                return
            # compute today by app timezone
            tz = ZoneInfo(settings.app_timezone)
            today = datetime.datetime.now(tz).date()
            meals, total_cal, total_pro = self.meal_repo.day_summary(link.user_id, today)
            msg = today_summary_message(text, len(meals), total_cal, total_pro)
            await send_telegram_message(chat_id, msg)
            return

        if text.startswith("/link"):
            parts = text.split()
            if len(parts) != 2:
                await send_telegram_message(chat_id, "Usage: /link ABC123")
                return

            code = parts[1].strip().upper()
            code_hash = _hash_code(code)
            row = self.repo.get_code(code_hash)
            if not row:
                await send_telegram_message(chat_id, "Invalid link code.")
                return

            now = datetime.datetime.now(datetime.timezone.utc)
            if row.used_at is not None:
                await send_telegram_message(chat_id, "Link code already used.")
                return
            if now >= row.expires_at:
                await send_telegram_message(chat_id, "Link code expired.")
                return

            # block if user already linked
            if self.repo.get_link_by_user(row.user_id):
                await send_telegram_message(chat_id, "Already linked.")
                return

            # block if chat already linked
            if self.repo.get_link_by_chat(chat_id):
                await send_telegram_message(chat_id, "This Telegram chat is already linked.")
                return

            self.repo.create_link(user_id=row.user_id, chat_id=chat_id)
            self.repo.mark_code_used(row)
            await send_telegram_message(chat_id, "Linked successfully ✅")
            return

        # Otherwise: treat as meal text
        link = self.repo.get_link_by_chat(chat_id)
        if not link:
            await send_telegram_message(chat_id, "Not linked. Use /link <code> from the app.")
            return

        meal = self.meal_service.analyze_and_create(link.user_id, text)
        items = [
            {
                "name": it.name,
                "quantity": float(it.quantity) if it.quantity is not None else None,
                "unit": it.unit,
                "calories": int(it.calories),
                "protein_g": float(it.protein_g),
                "position": int(it.position),
            }
            for it in sorted(meal.items, key=lambda x: x.position)
        ]
        msg = meal_added_message(text, meal.title, int(meal.total_calories), float(meal.total_protein_g), items)
        await send_telegram_message(chat_id, msg)

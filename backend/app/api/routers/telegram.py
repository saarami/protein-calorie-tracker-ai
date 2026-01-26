from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.core.config import settings
from app.core.errors import http_error, ErrorCodes
from app.db.session import get_db
from app.schemas.telegram import LinkCodeResponse, TelegramStatusResponse
from app.services.telegram.service import TelegramService

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


@router.post("/link-code", response_model=LinkCodeResponse)
def create_link_code(db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = TelegramService(db)
    code = svc.create_link_code(user.id)
    return LinkCodeResponse(code=code, expires_in=600)


@router.get("/status", response_model=TelegramStatusResponse)
def status(db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = TelegramService(db)
    st = svc.status(user.id)
    return TelegramStatusResponse(**st)


@router.post("/webhook")
async def webhook(
    request: Request,
    db: Session = Depends(get_db),
    telegram_secret_token: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
):
    # Telegram sends the webhook secret in this header when you set `secret_token` in setWebhook:
    # X-Telegram-Bot-Api-Secret-Token
    if not settings.telegram_webhook_secret or settings.telegram_webhook_secret == "change_me":
        raise http_error(500, ErrorCodes.TELEGRAM_WEBHOOK_UNAUTHORIZED, "Webhook secret not configured")

    if telegram_secret_token != settings.telegram_webhook_secret:
        raise http_error(401, ErrorCodes.TELEGRAM_WEBHOOK_UNAUTHORIZED, "Unauthorized")

    update = await request.json()
    svc = TelegramService(db)
    await svc.handle_update(update)
    return {"ok": True}

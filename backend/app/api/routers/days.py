from __future__ import annotations

import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.schemas.day import DaySummaryOut
from app.services.days.day_service import DayService

router = APIRouter(prefix="/api/v1/days", tags=["days"])


@router.get("/today", response_model=DaySummaryOut)
def today(db: Session = Depends(get_db), user=Depends(get_current_user)) -> DaySummaryOut:
    tz = ZoneInfo(settings.app_timezone)
    today_date = datetime.datetime.now(tz).date()
    return DayService(db).get_day_summary(user=user, date=today_date)


@router.get("/{date}", response_model=DaySummaryOut)
def get_by_date(
    date: datetime.date,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> DaySummaryOut:
    return DayService(db).get_day_summary(user=user, date=date)

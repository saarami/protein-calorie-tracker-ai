from __future__ import annotations
import os
from typing import Any
from decimal import Decimal
from zoneinfo import ZoneInfo
import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.repositories.meal_repository import MealRepository
from app.schemas.day import DaySummaryOut
from app.schemas.day import DayGoals, DayMealBrief, DayProgress, DaySummaryOut
from app.schemas.meal import MealTotals
from app.infra.redis.cache import cache_get_str, cache_set_str
from app.infra.redis.keys import day_summary_key



router = APIRouter(prefix="/api/v1/days", tags=["days"])


def _calc_progress(total: float, goal: float | None) -> float | None:
    if goal is None or goal <= 0:
        return None
    return round((total / goal) * 100.0, 2)


def _build_day_summary(db: Session, user, date: datetime.date) -> DaySummaryOut:
    repo = MealRepository(db)
    meals, total_cal, total_pro = repo.day_summary(user.id, date)

    goals = DayGoals(
        calories=user.goal_calories,
        protein_g=float(user.goal_protein_g) if user.goal_protein_g is not None else None,
    )

    progress = DayProgress(
        calories_pct=_calc_progress(
            float(total_cal),
            float(goals.calories) if goals.calories is not None else None,
        ),
        protein_pct=_calc_progress(
            float(total_pro),
            float(goals.protein_g) if goals.protein_g is not None else None,
        ),
    )

    meal_briefs = [
        DayMealBrief(
            id=m.id,
            title=m.title,
            totals=MealTotals(
                calories=int(m.total_calories),
                protein_g=float(m.total_protein_g),
            ),
        )
        for m in meals
    ]

    return DaySummaryOut(
        date=date,
        meals_count=len(meals),
        totals=MealTotals(
            calories=int(total_cal),
            protein_g=float(total_pro),
        ),
        goals=goals,
        progress=progress,
        meals=meal_briefs,
    )


def _day_summary_cache_key(user_id: Any, date: datetime.date) -> str:
    return f"day_summary:v1:{user_id}:{date.isoformat()}"


def _get_day_summary_cached(db: Session, user, date: datetime.date) -> DaySummaryOut:
    ttl = int(os.getenv("DAY_SUMMARY_CACHE_TTL_SECONDS", "120"))
    key = _day_summary_cache_key(user.id, date)

    cached = cache_get_str(key)
    if cached:
        print("[CACHE HIT]", key)
        return DaySummaryOut.model_validate_json(cached)
    print("[CACHE MISS]", key)
    if cached:
        return DaySummaryOut.model_validate_json(cached)

    result = _build_day_summary(db=db, user=user, date=date)

    cache_set_str(key, result.model_dump_json(), ttl_seconds=ttl)
    return result


    return DaySummaryOut(
        date=date,
        meals_count=len(meals),
        totals=MealTotals(calories=int(total_cal), protein_g=float(total_pro)),
        goals=goals,
        progress=progress,
        meals=meal_briefs,
    )


@router.get("/today", response_model=DaySummaryOut)
def today(db: Session = Depends(get_db), user=Depends(get_current_user)) -> DaySummaryOut:
    tz = ZoneInfo(settings.app_timezone)
    d = datetime.datetime.now(tz).date()
    return _get_day_summary_cached(db=db, user=user, date=d)



@router.get("/{date}", response_model=DaySummaryOut)
def get_by_date(
    date: datetime.date,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> DaySummaryOut:
    return _get_day_summary_cached(db=db, user=user, date=date)


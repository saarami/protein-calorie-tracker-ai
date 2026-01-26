from __future__ import annotations

import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.repositories.meal_repository import MealRepository
from app.schemas.day import DayGoals, DayMealBrief, DayProgress, DaySummaryOut
from app.schemas.meal import MealTotals
from decimal import Decimal

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
    print(type(total_cal), type(goals.calories), type(total_pro), type(goals.protein_g))
    progress = DayProgress(
        calories_pct=_calc_progress(float(total_cal), float(goals.calories)),
        protein_pct=_calc_progress(float(total_pro), float(goals.protein_g)),
    )
    meal_briefs = [
        DayMealBrief(
            id=m.id,
            title=m.title,
            totals=MealTotals(calories=int(m.total_calories), protein_g=float(m.total_protein_g)),
        )
        for m in meals
    ]

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
    return _build_day_summary(db=db, user=user, date=d)


@router.get("/{date}", response_model=DaySummaryOut)
def get_by_date(
    date: datetime.date,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> DaySummaryOut:
    return _build_day_summary(db=db, user=user, date=date)

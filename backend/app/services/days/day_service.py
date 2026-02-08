from __future__ import annotations

import os
import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.infra.redis.cache import cache_get_str, cache_set_str
from app.infra.redis.keys import day_summary_key
from app.repositories.meal_repository import MealRepository
from app.schemas.day import DayGoals, DayMealBrief, DayProgress, DaySummaryOut
from app.schemas.meal import MealTotals


def _calc_progress(total: float, goal: float | None) -> float | None:
    if goal is None or goal <= 0:
        return None
    return round((total / goal) * 100.0, 2)


class DayService:
    def __init__(self, db: Session):
        self.db = db
        self.meal_repo = MealRepository(db)

    def _build_day_summary(self, user: Any, date: datetime.date) -> DaySummaryOut:
        meals, total_cal, total_pro = self.meal_repo.day_summary(user.id, date)

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

    def get_day_summary(self, user: Any, date: datetime.date) -> DaySummaryOut:
        ttl_seconds = int(os.getenv("DAY_SUMMARY_CACHE_TTL_SECONDS", "120"))
        key = day_summary_key(user.id, date)

        cached = cache_get_str(key)
        if cached:
            return DaySummaryOut.model_validate_json(cached)

        result = self._build_day_summary(user=user, date=date)
        cache_set_str(key, result.model_dump_json(), ttl_seconds=ttl_seconds)
        return result

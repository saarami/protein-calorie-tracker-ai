from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel

from app.schemas.meal import MealTotals


class DayMealBrief(BaseModel):
    id: uuid.UUID
    title: str
    totals: MealTotals


class DayGoals(BaseModel):
    calories: int | None = None
    protein_g: float | None = None


class DayProgress(BaseModel):
    calories_pct: float | None = None
    protein_pct: float | None = None


class DaySummaryOut(BaseModel):
    date: datetime.date
    meals_count: int
    totals: MealTotals
    goals: DayGoals
    progress: DayProgress
    meals: list[DayMealBrief]

from __future__ import annotations

import datetime
import logging
import uuid
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ErrorCodes, http_error
from app.repositories.meal_repository import MealRepository
from app.services.openai.meal_parser import ParsedMeal, parse_meal

logger = logging.getLogger(__name__)


def _today_local_date() -> datetime.date:
    tz = ZoneInfo(settings.app_timezone)
    return datetime.datetime.now(tz).date()


class MealService:
    def __init__(self, db: Session):
        self.repo = MealRepository(db)

    def analyze_and_create(self, user_id: uuid.UUID, text: str):
        try:
            parsed: ParsedMeal = parse_meal(text)
        except Exception:
            logger.exception("Meal parsing failed (OpenAI)")
            raise http_error(502, ErrorCodes.MEAL_PARSE_FAILED, "Meal parsing failed")

        meal_date = _today_local_date()

        return self.repo.create_meal_with_items(
            user_id=user_id,
            raw_text=text,
            title=parsed.title,
            total_calories=parsed.totals.calories,
            total_protein_g=Decimal(parsed.totals.protein_g),
            meal_date=meal_date,
            items=[it.model_dump() for it in parsed.items],
        )

    def get(self, meal_id: uuid.UUID):
        meal = self.repo.get_by_id(meal_id)
        if meal is None:
            raise http_error(404, ErrorCodes.MEAL_NOT_FOUND, "Meal not found")
        return meal

    def list(self, user_id: uuid.UUID, date: datetime.date | None, limit: int, offset: int):
        return self.repo.list_by_user(user_id=user_id, date=date, limit=limit, offset=offset)

    def delete(self, meal_id: uuid.UUID) -> None:
        meal = self.get(meal_id)
        self.repo.delete(meal)

    def patch(self, meal_id: uuid.UUID, title: str | None, items: list[dict] | None):
        meal = self.get(meal_id)

        if items is not None:
            meal.total_calories = sum(it["calories"] for it in items)
            meal.total_protein_g = sum(Decimal(it["protein_g"]) for it in items)

        return self.repo.patch(meal, title=title, items=items)

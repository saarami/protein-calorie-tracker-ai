from __future__ import annotations

import datetime
import uuid
from decimal import Decimal
from typing import Iterable

from sqlalchemy.orm import Session, selectinload

from app.models.meal import Meal
from app.models.meal_item import MealItem


class MealRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_meal_with_items(
        self,
        *,
        user_id: uuid.UUID,
        raw_text: str,
        title: str,
        total_calories: int,
        total_protein_g: Decimal,
        meal_date: datetime.date,
        items: Iterable[dict],
    ) -> Meal:
        meal = Meal(
            user_id=user_id,
            raw_text=raw_text,
            title=title,
            total_calories=total_calories,
            total_protein_g=total_protein_g,
            meal_date=meal_date,
        )
        self.db.add(meal)
        self.db.flush()  # populate meal.id

        for idx, it in enumerate(items):
            self.db.add(
                MealItem(
                    meal_id=meal.id,
                    name=it["name"],
                    quantity=it.get("quantity"),
                    unit=it.get("unit"),
                    calories=it["calories"],
                    protein_g=it["protein_g"],
                    position=idx,
                )
            )

        self.db.commit()
        self.db.refresh(meal)
        return meal

    def get_by_id(self, meal_id: uuid.UUID) -> Meal | None:
        return (
            self.db.query(Meal)
            .options(selectinload(Meal.items))
            .filter(Meal.id == meal_id)
            .one_or_none()
        )

    def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        date: datetime.date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Meal]:
        q = (
            self.db.query(Meal)
            .options(selectinload(Meal.items))
            .filter(Meal.user_id == user_id)
        )
        if date is not None:
            q = q.filter(Meal.meal_date == date)

        return (
            q.order_by(Meal.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def delete(self, meal: Meal) -> None:
        self.db.delete(meal)
        self.db.commit()

    def patch(
        self,
        meal: Meal,
        *,
        title: str | None,
        items: Iterable[dict] | None,
    ) -> Meal:
        if title is not None:
            meal.title = title

        if items is not None:
            meal.items.clear()
            self.db.flush()
            for idx, it in enumerate(items):
                meal.items.append(
                    MealItem(
                        meal_id=meal.id,
                        name=it["name"],
                        quantity=it.get("quantity"),
                        unit=it.get("unit"),
                        calories=it["calories"],
                        protein_g=it["protein_g"],
                        position=idx,
                    )
                )

        self.db.commit()
        self.db.refresh(meal)
        return meal

    def day_summary(
        self,
        user_id: uuid.UUID,
        date: datetime.date,
    ) -> tuple[list[Meal], int, Decimal]:
        meals = (
            self.db.query(Meal)
            .options(selectinload(Meal.items))
            .filter(Meal.user_id == user_id, Meal.meal_date == date)
            .order_by(Meal.created_at.asc())
            .all()
        )

        total_calories = sum(m.total_calories for m in meals)
        total_protein = sum(m.total_protein_g for m in meals)

        return meals, total_calories, total_protein

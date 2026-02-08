# backend/app/api/routers/meals.py
from __future__ import annotations

import datetime
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.meal import MealCreateRequest, MealOut, MealPatchRequest
from app.services.meals.meal_service import MealService
from app.infra.redis.cache import cache_delete
from app.infra.redis.keys import day_summary_key

router = APIRouter(prefix="/api/v1/meals", tags=["meals"])


def _meal_out(meal) -> MealOut:
    out = MealOut.model_validate(meal)
    # Ensure stable ordering
    out = out.model_copy(update={"items": sorted(out.items, key=lambda x: x.position)})
    return out


@router.post("", response_model=MealOut)
def create(
    payload: MealCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MealOut:
    service = MealService(db)
    meal = service.analyze_and_create(user.id, payload.text)
    cache_delete(day_summary_key(user.id, meal.meal_date))
    return _meal_out(meal)


@router.get("", response_model=list[MealOut])
def list_meals(
    date: str | None = Query(default=None, description="YYYY-MM-DD"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[MealOut]:
    parsed_date = datetime.date.fromisoformat(date) if date else None
    meals = MealService(db).list(user.id, parsed_date, limit=limit, offset=offset)
    return [_meal_out(m) for m in meals]


@router.patch("/{meal_id}", response_model=MealOut)
def patch(
    meal_id: uuid.UUID,
    payload: MealPatchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MealOut:
    service = MealService(db)
    meal = service.patch(
        meal_id,
        user.id,
        title=payload.title,
        items=[it.model_dump() for it in payload.items] if payload.items else None,
    )
    cache_delete(day_summary_key(user.id, meal.meal_date))
    return _meal_out(meal)


@router.delete("/{meal_id}")
def delete(
    meal_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, bool]:
    service = MealService(db)
    meal = service.get_owned(meal_id, user.id)
    meal_date = meal.meal_date
    service.delete(meal_id, user.id)
    cache_delete(day_summary_key(user.id, meal_date))
    return {"ok": True}

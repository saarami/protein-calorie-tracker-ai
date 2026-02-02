from __future__ import annotations
import datetime
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.auth.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.meal import MealCreateRequest, MealItemOut, MealOut, MealPatchRequest, MealTotals
from app.services.meals.meal_service import MealService
from app.infra.redis.cache import cache_delete
from app.infra.redis.keys import day_summary_key

router = APIRouter(prefix="/api/v1/meals", tags=["meals"])


def _to_out(meal) -> MealOut:
    items = sorted(meal.items, key=lambda x: x.position)
    return MealOut(
        id=meal.id,
        title=meal.title,
        raw_text=meal.raw_text,
        meal_date=meal.meal_date,
        created_at=meal.created_at,
        totals=MealTotals(
            calories=int(meal.total_calories),
            protein_g=float(meal.total_protein_g),
        ),
        items=[
            MealItemOut(
                id=i.id,
                name=i.name,
                quantity=float(i.quantity) if i.quantity is not None else None,
                unit=i.unit,
                calories=int(i.calories),
                protein_g=float(i.protein_g),
                position=int(i.position),
            )
            for i in items
        ],
    )


@router.post("", response_model=MealOut)
def create(payload: MealCreateRequest,db: Session = Depends(get_db),user: User = Depends(get_current_user),) -> MealOut:
    service = MealService(db)
    meal = service.analyze_and_create(user.id, payload.text)
    cache_delete(day_summary_key(user.id, meal.meal_date))
    return _to_out(meal)



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
    return [_to_out(m) for m in meals]


@router.patch("/{meal_id}", response_model=MealOut)
def patch(meal_id: uuid.UUID,payload: MealPatchRequest,db: Session = Depends(get_db),user: User = Depends(get_current_user),) -> MealOut:
    service = MealService(db)
    meal = service.patch(meal_id,user.id,title=payload.title,items=[it.model_dump() for it in payload.items] if payload.items else None,)
    # invalidate day summary cache for that date
    cache_delete(day_summary_key(user.id, meal.meal_date))
    return _to_out(meal)



@router.delete("/{meal_id}")
def delete(meal_id: uuid.UUID,db: Session = Depends(get_db),user: User = Depends(get_current_user),) -> dict[str, bool]:
    service = MealService(db)
    meal = service.get_owned(meal_id, user.id)
    meal_date = meal.meal_date
    service.delete(meal_id, user.id)
    cache_delete(day_summary_key(user.id, meal_date))
    return {"ok": True}

from __future__ import annotations

import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class MealItemIn(BaseModel):
    name: str = Field(min_length=1)
    quantity: Decimal | None = None
    unit: str | None = None
    calories: int = Field(ge=0)
    protein_g: Decimal = Field(ge=0)


class MealItemOut(MealItemIn):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    position: int


class MealTotals(BaseModel):
    calories: int = Field(ge=0)
    protein_g: Decimal = Field(ge=0)


class MealCreateRequest(BaseModel):
    text: str = Field(min_length=1)


class MealPatchRequest(BaseModel):
    title: str | None = None
    items: list[MealItemIn] | None = None


class MealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    raw_text: str
    meal_date: datetime.date
    created_at: datetime.datetime
    items: list[MealItemOut]

    # Pulled from ORM, excluded from API output; used to compute `totals`.
    total_calories: Decimal | int = Field(exclude=True, repr=False)
    total_protein_g: Decimal = Field(exclude=True, repr=False)

    @computed_field
    @property
    def totals(self) -> MealTotals:
        return MealTotals(
            calories=int(self.total_calories),
            protein_g=self.total_protein_g,
        )

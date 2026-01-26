from __future__ import annotations

import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, EmailStr, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    goal_calories: int | None = None
    goal_protein_g: Decimal | None = None
    created_at: datetime.datetime


class UserGoalsUpdate(BaseModel):
    goal_calories: int | None = None
    goal_protein_g: Decimal | None = None

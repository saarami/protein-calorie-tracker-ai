from __future__ import annotations

import datetime
import uuid
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class MealItem(Base):
    __tablename__ = "meal_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    meal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("meals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    unit: Mapped[str | None] = mapped_column(Text, nullable=True)

    calories: Mapped[int] = mapped_column(Integer, nullable=False)
    protein_g: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    meal = relationship("Meal", back_populates="items")

    def __repr__(self) -> str:
        return f"<MealItem id={self.id} meal_id={self.meal_id} name={self.name}>"

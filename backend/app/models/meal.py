from __future__ import annotations

import datetime
import uuid
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)

    total_calories: Mapped[int] = mapped_column(Integer, nullable=False)
    total_protein_g: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)

    meal_date: Mapped[datetime.date] = mapped_column(Date, index=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    items = relationship(
        "MealItem",
        back_populates="meal",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Meal id={self.id} user_id={self.user_id} date={self.meal_date}>"

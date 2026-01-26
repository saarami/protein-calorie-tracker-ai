from __future__ import annotations

import datetime
import uuid
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)

    goal_calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goal_protein_g: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

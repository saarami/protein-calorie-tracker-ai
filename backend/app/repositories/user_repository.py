from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .one_or_none()
        )

    def create(self, *, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_goals(
        self,
        user: User,
        *,
        goal_calories: int | None,
        goal_protein_g: Decimal | None,
    ) -> User:
        if goal_calories is not None:
            user.goal_calories = goal_calories
        if goal_protein_g is not None:
            user.goal_protein_g = goal_protein_g

        self.db.commit()
        self.db.refresh(user)
        return user

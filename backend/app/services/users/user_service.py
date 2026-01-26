from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.models.user import User


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def update_goals(self, user: User, goal_calories: int | None, goal_protein_g: float | None) -> User:
        return self.repo.update_goals(user,goal_calories=goal_calories,goal_protein_g=goal_protein_g,)

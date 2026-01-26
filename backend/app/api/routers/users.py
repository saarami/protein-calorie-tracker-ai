from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db.session import get_db
from app.schemas.user import UserOut, UserGoalsUpdate
from app.services.users.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.patch("/me", response_model=UserOut)
def update_me(payload: UserGoalsUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = UserService(db)
    updated = svc.update_goals(user, payload.goal_calories, payload.goal_protein_g)
    return UserOut.model_validate(updated)

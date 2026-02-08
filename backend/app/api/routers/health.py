from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.infra.redis.client import get_redis_client

router = APIRouter(tags=["health"])



@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    # Check DB
    db.execute(text("SELECT 1"))

    # Check Redis
    redis_client = get_redis_client()
    redis_client.ping()

    return {"status": "healthy"}
from __future__ import annotations
from typing import Optional
from app.infra.redis.client import get_redis_client

def cache_get_str(key: str) -> Optional[str]:
    r = get_redis_client()
    if r is None:
        return None
    return r.get(key)

def cache_set_str(key: str, value: str, ttl_seconds: int) -> None:
    r = get_redis_client()
    if r is None:
        return
    r.setex(key, ttl_seconds, value)

def cache_delete(key: str) -> None:
    r = get_redis_client()
    if r is None:
        return
    r.delete(key)

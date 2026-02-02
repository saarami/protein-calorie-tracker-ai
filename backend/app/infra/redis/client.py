import os
from functools import lru_cache
from typing import Optional

import redis


@lru_cache(maxsize=1)
def get_redis_client() -> Optional[redis.Redis]:
    enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"
    if not enabled:
        return None

    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    db = int(os.getenv("REDIS_DB", "0"))

    return redis.Redis(
        host=host,
        port=port,
        db=db,
        decode_responses=True,
    )

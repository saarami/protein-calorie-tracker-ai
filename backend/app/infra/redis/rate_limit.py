from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional, Tuple

import redis

from app.infra.redis.client import get_redis_client


LUA_TOKEN_BUCKET = r"""
-- KEYS[1] = key
-- ARGV[1] = now (float seconds)
-- ARGV[2] = capacity (float)
-- ARGV[3] = refill_per_sec (float)
-- ARGV[4] = expire_seconds (int)

local key = KEYS[1]
local now = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local refill_per_sec = tonumber(ARGV[3])
local expire_seconds = tonumber(ARGV[4])

local data = redis.call("HMGET", key, "tokens", "ts")
local tokens = tonumber(data[1])
local ts = tonumber(data[2])

if tokens == nil then
  tokens = capacity
end
if ts == nil then
  ts = now
end

-- refill
local delta = now - ts
if delta < 0 then
  delta = 0
end

tokens = math.min(capacity, tokens + (delta * refill_per_sec))

local allowed = 0
if tokens >= 1 then
  allowed = 1
  tokens = tokens - 1
end

-- persist
redis.call("HMSET", key, "tokens", tokens, "ts", now)
redis.call("EXPIRE", key, expire_seconds)

-- compute reset_after (seconds until next token available)
local reset_after = 0
if tokens < 1 then
  reset_after = math.ceil((1 - tokens) / refill_per_sec)
end

return {allowed, tokens, reset_after}
"""


@dataclass(frozen=True)
class RateLimitRule:
    name: str
    capacity: float
    refill_per_sec: float


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_after_seconds: int
    limit: int


class TokenBucketLimiter:
    def __init__(self) -> None:
        self._script: Optional[redis.client.Script] = None

    def _get_script(self, r: redis.Redis) -> redis.client.Script:
        if self._script is None:
            self._script = r.register_script(LUA_TOKEN_BUCKET)
        return self._script

    def allow(self, key: str, rule: RateLimitRule) -> Optional[RateLimitResult]:
        r = get_redis_client()
        if r is None:
            return None

        expire_seconds = int(os.getenv("RL_KEY_EXPIRE_SECONDS", "600"))
        now = time.time()

        script = self._get_script(r)
        allowed, tokens_left, reset_after = script(
            keys=[key],
            args=[now, rule.capacity, rule.refill_per_sec, expire_seconds],
        )

        # tokens_left is float; we expose int remaining (floor)
        remaining = int(tokens_left) if tokens_left is not None else 0

        return RateLimitResult(
            allowed=(int(allowed) == 1),
            remaining=max(0, remaining),
            reset_after_seconds=int(reset_after) if reset_after is not None else 0,
            limit=int(rule.capacity),
        )


def build_rl_key(rule_name: str, identifier: str, route_group: str) -> str:
    return f"rl:tb:{rule_name}:{identifier}:{route_group}"


def global_rule_from_env() -> RateLimitRule:
    cap = float(os.getenv("RL_GLOBAL_CAPACITY", "300.0"))
    refill = float(os.getenv("RL_GLOBAL_REFILL_PER_SEC", "1.0"))
    return RateLimitRule(name="global", capacity=cap, refill_per_sec=refill)


def meals_create_rule() -> RateLimitRule:
    # Example: 10 requests per minute
    return RateLimitRule(name="meals_create", capacity=10.0, refill_per_sec=(10.0 / 60.0))


def auth_login_rule() -> RateLimitRule:
    # Example: 10 per 5 minutes
    return RateLimitRule(name="auth_login", capacity=10.0, refill_per_sec=(10.0 / 300.0))


def auth_register_rule() -> RateLimitRule:
    # Example: 5 per hour
    return RateLimitRule(name="auth_register", capacity=5.0, refill_per_sec=(5.0 / 3600.0))

from __future__ import annotations

import os

import anyio
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings

from app.infra.redis.rate_limit import (
    TokenBucketLimiter,
    build_rl_key,
    global_rule_from_env,
    meals_create_rule,
    auth_login_rule,
    auth_register_rule,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.limiter = TokenBucketLimiter()

    def _get_identifier(self, request: Request) -> str:
        # Prefer authenticated user id if present (set by your auth dependency later in endpoint).
        # Middleware runs before dependencies, so we cannot rely on current_user here.
        # Therefore: we do IP-based limiting in middleware, and (optionally) add per-user limiting in endpoints later.
        xff = request.headers.get("x-forwarded-for")
        if xff:
            # take first IP
            return f"ip:{xff.split(',')[0].strip()}"
        client = request.client.host if request.client else "unknown"
        return f"ip:{client}"

    def _route_group(self, request: Request) -> str:
        # Global bucket groups by "all"
        # Specific buckets group by "METHOD:PATH"
        return f"{request.method}:{request.url.path}"

    async def _check(self, key: str, rule):
        return await anyio.to_thread.run_sync(self.limiter.allow, key, rule)

    async def dispatch(self, request: Request, call_next):
        if request.method.upper() == "OPTIONS":
            return await call_next(request)
        if not self.enabled:
            return await call_next(request)
        path = request.url.path
        if path == "/health":
            return await call_next(request)
        if path.endswith("/telegram/webhook"):
            return await call_next(request)

        identifier = self._get_identifier(request)
        # 1) Global rule for everything (soft)
        global_rule = global_rule_from_env()
        global_key = build_rl_key(global_rule.name, identifier, "all")
        global_res = await self._check(global_key, global_rule)

        if global_res is not None and not global_res.allowed:
            return JSONResponse(
                status_code=429,
                content={"code": "RATE_LIMITED", "message": "Too many requests"},
                headers={
                    "X-RateLimit-Limit": str(global_res.limit),
                    "X-RateLimit-Remaining": str(global_res.remaining),
                    "X-RateLimit-Reset": str(global_res.reset_after_seconds),
                },
            )

        # 2) Per-route stricter rules (hard)
        path = request.url.path
        method = request.method.upper()
        route_group = self._route_group(request)

        rule = None
        if method == "POST" and path == "/api/v1/meals":
            rule = meals_create_rule()
        elif method == "POST" and path == "/auth/login":
            rule = auth_login_rule()
        elif method == "POST" and path == "/auth/register":
            rule = auth_register_rule()




        if rule is not None:
            key = build_rl_key(rule.name, identifier, route_group)
            res = await self._check(key, rule)

            if res is not None and not res.allowed:
                return JSONResponse(
                    status_code=429,
                    content={"code": "RATE_LIMITED", "message": "Too many requests"},
                    headers={
                        "X-RateLimit-Limit": str(res.limit),
                        "X-RateLimit-Remaining": str(res.remaining),
                        "X-RateLimit-Reset": str(res.reset_after_seconds),
                    },
                )

        return await call_next(request)

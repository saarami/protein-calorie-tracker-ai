from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.days import router as days_router
from app.api.routers.health import router as health_router
from app.api.routers.meals import router as meals_router
from app.api.routers.telegram import router as telegram_router
from app.api.routers.users import router as users_router
from app.auth.router import router as auth_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import access_log_middleware, configure_logging
from app.middlewares.rate_limit import RateLimitMiddleware


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(title="protein-calorie-tracker", version="2.0.0")

    app.middleware("http")(access_log_middleware)
    app.add_middleware(RateLimitMiddleware)

    if settings.app_env == "local":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(meals_router)
    app.include_router(days_router)
    app.include_router(telegram_router)

    return app


app = create_app()

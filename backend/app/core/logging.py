from __future__ import annotations

import logging
import time
from typing import Callable

from fastapi import Request, Response

from app.core.config import settings


def configure_logging() -> None:
    """
    Central logging configuration.
    Should be called once on application startup.
    """
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


async def access_log_middleware(request: Request, call_next: Callable) -> Response:
    """
    Simple access log middleware.
    Logs method, path, status code and request duration.
    """
    logger = logging.getLogger("access")

    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s -> %s (%.2fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response

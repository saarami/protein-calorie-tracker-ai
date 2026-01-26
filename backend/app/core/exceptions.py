from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict) and "code" in exc.detail and "message" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)

        return JSONResponse(
            status_code=exc.status_code,
            content={"code": "HTTP_ERROR", "message": str(exc.detail)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, __: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"code": "VALIDATION_ERROR", "message": "Invalid request"},
        )

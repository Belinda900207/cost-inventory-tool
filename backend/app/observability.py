"""Safe request telemetry. Never log bodies, query strings or exception text."""

import json
import logging
import os
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

logger = logging.getLogger("cost_inventory.requests")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class ApiError(Exception):
    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        details: Mapping[str, str | int] | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details


def error_response(
    request: Request,
    status: int,
    code: str,
    message: str,
    details: Mapping[str, str | int] | None = None,
) -> JSONResponse:
    error: dict[str, object] = {
        "code": code,
        "message": message,
        "request_id": request.state.request_id,
    }
    if details is not None:
        error["details"] = dict(details)
    return JSONResponse(
        status_code=status,
        content={"error": error},
    )


def install_observability(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def api_error(request: Request, exc: ApiError):
        return error_response(
            request, exc.status, exc.code, exc.message, details=exc.details
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, _exc: RequestValidationError):
        return error_response(request, 422, "validation_error", "Invalid request")

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        response = error_response(
            request, exc.status_code, "http_error", "Request failed"
        )
        if exc.headers:
            response.headers.update(exc.headers)
        return response

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        ids = request.headers.getlist("x-request-id")
        candidate = ids[0] if len(ids) == 1 else ""
        request.state.request_id = (
            candidate
            if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", candidate)
            else uuid4().hex
        )
        started = perf_counter()
        try:
            response = await call_next(request)
        except Exception:  # noqa: BLE001 - sanitize unexpected errors at HTTP boundary
            response = error_response(
                request, 500, "internal_error", "Internal server error"
            )
        response.headers["X-Request-ID"] = request.state.request_id
        route = request.scope.get("route")
        logger.info(
            json.dumps(
                {
                    "time": datetime.now(UTC).isoformat(),
                    "level": "ERROR" if response.status_code >= 500 else "INFO",
                    "service": "cost-inventory-api",
                    "environment": os.getenv("ENVIRONMENT", "development"),
                    "request_id": request.state.request_id,
                    "method": request.method,
                    "path": getattr(route, "path", "<unmatched>"),
                    "status": response.status_code,
                    "duration_ms": round((perf_counter() - started) * 1000, 3),
                    "message": "request completed",
                }
            )
        )
        return response

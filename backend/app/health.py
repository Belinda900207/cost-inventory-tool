from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.db import DatabaseCheck, get_database_check
from app.observability import error_response

router = APIRouter(prefix="/health", tags=["health"])
Check = Annotated[DatabaseCheck, Depends(get_database_check)]


@router.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("")
def readiness(response: Response, check: Check) -> dict[str, str]:
    try:
        check()
    except Exception:  # noqa: BLE001 - probe failures must never expose DB details
        response.status_code = 503
        return {"status": "unhealthy", "database": "unavailable"}
    return {"status": "ok", "database": "ok"}


@router.get("/ready")
def ready(request: Request, check: Check):
    try:
        check()
    except Exception:  # noqa: BLE001 - readiness must sanitize all probe failures
        return error_response(
            request, 503, "database_unavailable", "Database unavailable"
        )
    return {"status": "ok", "database": "ok"}

from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.db import DatabaseCheck, get_database_check

router = APIRouter(prefix="/health", tags=["health"])
Check = Annotated[DatabaseCheck, Depends(get_database_check)]


@router.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("")
@router.get("/ready")
def readiness(response: Response, check: Check) -> dict[str, str]:
    try:
        check()
    except Exception:  # noqa: BLE001 - probe failures must never expose DB details
        response.status_code = 503
        return {"status": "unhealthy", "database": "unavailable"}
    return {"status": "ok", "database": "ok"}

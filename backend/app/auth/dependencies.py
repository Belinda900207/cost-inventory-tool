from typing import Annotated

from fastapi import Depends, HTTPException, Request

from app.auth.schemas import Principal
from app.auth.service import AuthService


def get_auth_service() -> AuthService:
    raise HTTPException(status_code=501, detail="Authentication is not configured")


async def require_principal(
    request: Request, service: Annotated[AuthService, Depends(get_auth_service)]
) -> Principal:
    principal = await service.resolve_principal(request)
    if principal is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return principal

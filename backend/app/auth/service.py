from typing import Protocol

from fastapi import Request

from app.auth.schemas import LoginRequest, Principal


class AuthService(Protocol):
    """Interface only. No fake implementation or credential storage."""

    async def authenticate(self, credentials: LoginRequest) -> Principal | None: ...

    async def resolve_principal(self, request: Request) -> Principal | None: ...

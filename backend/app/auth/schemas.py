"""Proposed auth DTOs only; transport/session policy is intentionally undecided."""

from pydantic import BaseModel, SecretStr


class LoginRequest(BaseModel):
    identifier: str
    password: SecretStr


class Principal(BaseModel):
    subject: str
    display_name: str

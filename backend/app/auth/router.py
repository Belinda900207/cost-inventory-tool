from fastapi import APIRouter

# Deliberately no endpoints until authentication policy and storage are approved.
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

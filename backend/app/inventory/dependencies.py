from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.inventory.repository import InventoryRepository
from app.inventory.service import InventoryService


def get_inventory_service(
    session: Annotated[Session, Depends(get_session)],
) -> InventoryService:
    return InventoryService(InventoryRepository(session))

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.inventory.repository import InventoryRepository
from app.simulations.service import SimulationService


def get_simulation_service(
    session: Annotated[Session, Depends(get_session)],
) -> SimulationService:
    return SimulationService(InventoryRepository(session))

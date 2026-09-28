from typing import Annotated

from fastapi import APIRouter, Depends

from app.costing.engine import InsufficientInventory
from app.inventory.errors import ProductNotFound
from app.observability import ApiError
from app.simulations.dependencies import get_simulation_service
from app.simulations.schemas import (
    CostSimulationRequest,
    CostSimulationResponse,
    simulation_response,
)
from app.simulations.service import SimulationService

router = APIRouter(prefix="/api/v1", tags=["simulations"])
Service = Annotated[SimulationService, Depends(get_simulation_service)]


@router.post("/simulations/cost", response_model=CostSimulationResponse)
def simulate_cost(
    request: CostSimulationRequest, service: Service
) -> CostSimulationResponse:
    try:
        result = service.simulate(request)
    except ProductNotFound:
        raise ApiError(404, "product_not_found", "Product not found") from None
    except InsufficientInventory as exc:
        raise ApiError(
            409,
            "insufficient_inventory",
            "Insufficient inventory",
            details={"requested": exc.requested, "available": exc.available},
        ) from None
    return simulation_response(request, result)

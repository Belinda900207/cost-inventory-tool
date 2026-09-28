from app.costing.engine import (
    CostBatch,
    CostSimulationResult,
    calculate_cost_simulation,
)
from app.inventory.errors import ProductNotFound
from app.inventory.repository import InventoryRepository
from app.simulations.schemas import CostSimulationRequest


class SimulationService:
    def __init__(self, repository: InventoryRepository) -> None:
        self.repository = repository

    def simulate(self, request: CostSimulationRequest) -> CostSimulationResult:
        product = self.repository.get_inventory(request.product_id)
        if product is None:
            raise ProductNotFound
        batches = [
            CostBatch(
                batch_id=item.id,
                remaining_quantity=item.remaining_quantity,
                unit_cost=item.unit_cost,
                purchased_at=item.purchased_at,
            )
            for item in product.batches
        ]
        return calculate_cost_simulation(
            batches,
            quantity=request.quantity,
            selling_unit_price=request.selling_unit_price,
        )

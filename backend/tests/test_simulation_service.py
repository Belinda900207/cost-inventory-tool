from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock, call

import pytest

from app.costing.engine import InsufficientInventory
from app.inventory.errors import ProductNotFound
from app.inventory.models import Product, PurchaseBatch
from app.simulations.schemas import CostSimulationRequest
from app.simulations.service import SimulationService


def product_with_batches() -> Product:
    product = Product(id=1, name="Product A", normalized_name="product a")
    product.batches = [
        PurchaseBatch(
            id=2,
            product_id=1,
            original_quantity=10,
            remaining_quantity=10,
            unit_cost=Decimal("100"),
            currency="CAD",
            purchased_at=datetime(2026, 9, 28, 1, 0, tzinfo=UTC),
        ),
        PurchaseBatch(
            id=1,
            product_id=1,
            original_quantity=20,
            remaining_quantity=20,
            unit_cost=Decimal("80"),
            currency="CAD",
            purchased_at=datetime(2026, 9, 27, 1, 0, tzinfo=UTC),
        ),
    ]
    return product


def request(quantity: int = 25) -> CostSimulationRequest:
    return CostSimulationRequest(
        product_id=1,
        quantity=quantity,
        selling_unit_price=Decimal("120"),
        currency="CAD",
    )


def test_simulation_service_only_reads_inventory():
    repository = MagicMock()
    repository.get_inventory.return_value = product_with_batches()

    result = SimulationService(repository).simulate(request())

    assert result.fifo.total_cost == Decimal("2100")
    assert repository.method_calls == [call.get_inventory(1)]


def test_simulation_service_requires_product():
    repository = MagicMock()
    repository.get_inventory.return_value = None

    with pytest.raises(ProductNotFound):
        SimulationService(repository).simulate(request())


def test_simulation_service_propagates_safe_inventory_shortage():
    repository = MagicMock()
    repository.get_inventory.return_value = product_with_batches()

    with pytest.raises(InsufficientInventory) as caught:
        SimulationService(repository).simulate(request(quantity=31))

    assert (caught.value.requested, caught.value.available) == (31, 30)

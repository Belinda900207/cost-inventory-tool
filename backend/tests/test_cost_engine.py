from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.costing.engine import (
    CostBatch,
    InsufficientInventory,
    calculate_cost_simulation,
)


def batch(
    batch_id: int,
    quantity: int,
    unit_cost: str,
    purchased_at: datetime,
) -> CostBatch:
    return CostBatch(
        batch_id=batch_id,
        remaining_quantity=quantity,
        unit_cost=Decimal(unit_cost),
        purchased_at=purchased_at,
    )


EARLIER = datetime(2026, 9, 27, 1, 0, tzinfo=UTC)
LATER = datetime(2026, 9, 28, 1, 0, tzinfo=UTC)
GOLDEN_BATCHES = [
    batch(1, 20, "80.000000", EARLIER),
    batch(2, 10, "100.000000", LATER),
]


@pytest.mark.parametrize(
    ("quantity", "fifo_total"),
    [(1, "80"), (25, "2100"), (30, "2600")],
)
def test_golden_fifo_and_weighted_average_cases(quantity, fifo_total):
    result = calculate_cost_simulation(
        GOLDEN_BATCHES,
        quantity=quantity,
        selling_unit_price=Decimal("120.00"),
    )

    assert result.fifo.total_cost == Decimal(fifo_total)
    assert result.fifo.unit_cost == Decimal(fifo_total) / quantity
    assert result.weighted_average.unit_cost == Decimal("2600") / 30
    assert result.weighted_average.total_cost == Decimal("2600") / 30 * quantity
    assert result.revenue == Decimal("120") * quantity


def test_weighted_average_uses_quantity_weights_not_simple_average():
    result = calculate_cost_simulation(
        GOLDEN_BATCHES, quantity=1, selling_unit_price=Decimal("120")
    )

    assert result.weighted_average.unit_cost == Decimal("2600") / 30
    assert result.weighted_average.unit_cost != Decimal("90")


def test_fifo_orders_by_purchase_time_then_batch_id_and_ignores_empty_batches():
    same_time = datetime(2026, 9, 27, 2, 0, tzinfo=UTC)
    batches = [
        batch(3, 0, "1", EARLIER),
        batch(2, 1, "100", same_time),
        batch(1, 1, "80", same_time),
    ]

    result = calculate_cost_simulation(
        batches, quantity=1, selling_unit_price=Decimal("120")
    )

    assert result.fifo.total_cost == Decimal("80")


def test_insufficient_inventory_returns_no_partial_result():
    with pytest.raises(InsufficientInventory) as caught:
        calculate_cost_simulation(
            GOLDEN_BATCHES, quantity=31, selling_unit_price=Decimal("120")
        )

    assert caught.value.requested == 31
    assert caught.value.available == 30


def test_repeated_simulation_is_deterministic_and_does_not_mutate_inputs():
    before = tuple(GOLDEN_BATCHES)

    results = [
        calculate_cost_simulation(
            GOLDEN_BATCHES, quantity=25, selling_unit_price=Decimal("120")
        )
        for _ in range(10)
    ]

    assert all(result == results[0] for result in results)
    assert tuple(GOLDEN_BATCHES) == before

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Literal

CostMethod = Literal["fifo", "weighted_average"]
ComparedMethod = Literal["fifo", "weighted_average", "equal"]


@dataclass(frozen=True)
class CostBatch:
    batch_id: int
    remaining_quantity: int
    unit_cost: Decimal
    purchased_at: datetime


class InsufficientInventory(Exception):
    def __init__(self, requested: int, available: int) -> None:
        super().__init__("Insufficient inventory")
        self.requested = requested
        self.available = available


@dataclass(frozen=True)
class MethodResult:
    method: CostMethod
    unit_cost: Decimal
    total_cost: Decimal
    gross_profit: Decimal
    gross_margin_percent: Decimal


@dataclass(frozen=True)
class DifferenceValue:
    amount: Decimal
    higher_method: ComparedMethod


@dataclass(frozen=True)
class CostDifference:
    total_cost: DifferenceValue
    gross_profit: DifferenceValue


@dataclass(frozen=True)
class CostSimulationResult:
    quantity: int
    selling_unit_price: Decimal
    revenue: Decimal
    fifo: MethodResult
    weighted_average: MethodResult
    difference: CostDifference


def _method_result(
    method: CostMethod,
    total_cost: Decimal,
    quantity: int,
    revenue: Decimal,
    *,
    unit_cost: Decimal | None = None,
) -> MethodResult:
    gross_profit = revenue - total_cost
    return MethodResult(
        method=method,
        unit_cost=unit_cost
        if unit_cost is not None
        else total_cost / Decimal(quantity),
        total_cost=total_cost,
        gross_profit=gross_profit,
        gross_margin_percent=gross_profit / revenue * Decimal("100"),
    )


def _difference(fifo_value: Decimal, weighted_value: Decimal) -> DifferenceValue:
    if fifo_value == weighted_value:
        higher_method: ComparedMethod = "equal"
    elif fifo_value > weighted_value:
        higher_method = "fifo"
    else:
        higher_method = "weighted_average"
    return DifferenceValue(
        amount=abs(fifo_value - weighted_value), higher_method=higher_method
    )


def calculate_cost_simulation(
    batches: list[CostBatch],
    *,
    quantity: int,
    selling_unit_price: Decimal,
) -> CostSimulationResult:
    """Calculate both methods without mutating inputs or touching persistence."""
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    if selling_unit_price <= 0:
        raise ValueError("selling_unit_price must be positive")
    if any(item.remaining_quantity < 0 or item.unit_cost <= 0 for item in batches):
        raise ValueError("batch values must be valid")

    available = sum(item.remaining_quantity for item in batches)
    if available < quantity:
        raise InsufficientInventory(quantity, available)

    eligible = [item for item in batches if item.remaining_quantity > 0]
    remaining = quantity
    fifo_total = Decimal("0")
    for item in sorted(
        eligible, key=lambda value: (value.purchased_at, value.batch_id)
    ):
        taken = min(remaining, item.remaining_quantity)
        fifo_total += Decimal(taken) * item.unit_cost
        remaining -= taken
        if remaining == 0:
            break

    inventory_cost = sum(
        (Decimal(item.remaining_quantity) * item.unit_cost for item in eligible),
        start=Decimal("0"),
    )
    weighted_unit = inventory_cost / Decimal(available)
    weighted_total = weighted_unit * Decimal(quantity)
    revenue = Decimal(quantity) * selling_unit_price
    fifo = _method_result("fifo", fifo_total, quantity, revenue)
    weighted_average = _method_result(
        "weighted_average",
        weighted_total,
        quantity,
        revenue,
        unit_cost=weighted_unit,
    )
    return CostSimulationResult(
        quantity=quantity,
        selling_unit_price=selling_unit_price,
        revenue=revenue,
        fifo=fifo,
        weighted_average=weighted_average,
        difference=CostDifference(
            total_cost=_difference(fifo.total_cost, weighted_average.total_cost),
            gross_profit=_difference(fifo.gross_profit, weighted_average.gross_profit),
        ),
    )

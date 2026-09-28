from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field, PositiveInt, field_serializer

from app.costing.engine import CostSimulationResult

MoneyInput = Annotated[Decimal, Field(gt=0, max_digits=19, decimal_places=6)]
DISCLAIMER = "此結果僅供成本比較，不是正式會計淨利。"


def display_decimal(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f")


class CostSimulationRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: PositiveInt
    selling_unit_price: MoneyInput
    currency: Literal["CAD"]


class MethodResultResponse(BaseModel):
    method: Literal["fifo", "weighted_average"]
    unit_cost: Decimal
    total_cost: Decimal
    gross_profit: Decimal
    gross_margin_percent: Decimal

    @field_serializer("unit_cost", "total_cost", "gross_profit", "gross_margin_percent")
    def serialize_decimal(self, value: Decimal) -> str:
        return display_decimal(value)


class DifferenceValueResponse(BaseModel):
    amount: Decimal
    higher_method: Literal["fifo", "weighted_average", "equal"]

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> str:
        return display_decimal(value)


class DifferenceResponse(BaseModel):
    total_cost: DifferenceValueResponse
    gross_profit: DifferenceValueResponse


class CostSimulationResponse(BaseModel):
    product_id: int
    quantity: int
    currency: Literal["CAD"]
    selling_unit_price: Decimal
    revenue: Decimal
    fifo: MethodResultResponse
    weighted_average: MethodResultResponse
    difference: DifferenceResponse
    inventory_changed: Literal[False] = False
    disclaimer: str = DISCLAIMER

    @field_serializer("selling_unit_price", "revenue")
    def serialize_money(self, value: Decimal) -> str:
        return display_decimal(value)


def simulation_response(
    request: CostSimulationRequest, result: CostSimulationResult
) -> CostSimulationResponse:
    return CostSimulationResponse(
        product_id=request.product_id,
        quantity=request.quantity,
        currency=request.currency,
        selling_unit_price=result.selling_unit_price,
        revenue=result.revenue,
        fifo=MethodResultResponse(**result.fifo.__dict__),
        weighted_average=MethodResultResponse(**result.weighted_average.__dict__),
        difference=DifferenceResponse(
            total_cost=DifferenceValueResponse(**result.difference.total_cost.__dict__),
            gross_profit=DifferenceValueResponse(
                **result.difference.gross_profit.__dict__
            ),
        ),
    )

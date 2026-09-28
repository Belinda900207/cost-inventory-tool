from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    field_serializer,
    field_validator,
)

MoneyInput = Annotated[Decimal, Field(gt=0, max_digits=19, decimal_places=6)]


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def display_money(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f")


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def trim_nonempty_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Product name cannot be blank")
        return trimmed


class ProductResponse(BaseModel):
    product_id: int
    name: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_timestamp(self, value: datetime) -> str:
        return ensure_utc(value).isoformat().replace("+00:00", "Z")


class PurchaseBatchCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: PositiveInt
    unit_cost: MoneyInput
    currency: Literal["CAD"]
    purchased_at: datetime

    @field_validator("purchased_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("purchased_at must include a timezone")
        return value.astimezone(UTC)


class PurchaseBatchResponse(BaseModel):
    batch_id: int
    product_id: int
    original_quantity: int
    remaining_quantity: int
    unit_cost: Decimal
    currency: Literal["CAD"]
    purchased_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("unit_cost")
    def serialize_unit_cost(self, value: Decimal) -> str:
        return display_money(value)

    @field_serializer("purchased_at", "created_at", "updated_at")
    def serialize_timestamp(self, value: datetime) -> str:
        return ensure_utc(value).isoformat().replace("+00:00", "Z")


class InventoryBatchResponse(BaseModel):
    batch_id: int
    original_quantity: int
    remaining_quantity: int
    unit_cost: Decimal
    currency: Literal["CAD"]
    purchased_at: datetime

    @field_serializer("unit_cost")
    def serialize_unit_cost(self, value: Decimal) -> str:
        return display_money(value)

    @field_serializer("purchased_at")
    def serialize_timestamp(self, value: datetime) -> str:
        return ensure_utc(value).isoformat().replace("+00:00", "Z")


class InventoryResponse(BaseModel):
    product_id: int
    product_name: str
    total_remaining_quantity: int
    batches: list[InventoryBatchResponse]

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utc_now_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint(
            "CHAR_LENGTH(normalized_name) > 0", name="ck_products_name_not_empty"
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    normalized_name: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=utc_now_naive,
        server_default=text("CURRENT_TIMESTAMP(6)"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=utc_now_naive,
        onupdate=utc_now_naive,
        server_default=text("CURRENT_TIMESTAMP(6)"),
    )
    batches: Mapped[list["PurchaseBatch"]] = relationship(
        back_populates="product",
        order_by="(PurchaseBatch.purchased_at, PurchaseBatch.id)",
    )


class PurchaseBatch(Base):
    __tablename__ = "purchase_batches"
    __table_args__ = (
        CheckConstraint(
            "original_quantity > 0", name="ck_purchase_batches_original_positive"
        ),
        CheckConstraint(
            "remaining_quantity >= 0",
            name="ck_purchase_batches_remaining_nonnegative",
        ),
        CheckConstraint(
            "remaining_quantity <= original_quantity",
            name="ck_purchase_batches_remaining_within_original",
        ),
        CheckConstraint("unit_cost > 0", name="ck_purchase_batches_cost_positive"),
        CheckConstraint("currency = 'CAD'", name="ck_purchase_batches_currency_cad"),
        Index("ix_purchase_batches_product_order", "product_id", "purchased_at", "id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    original_quantity: Mapped[int]
    remaining_quantity: Mapped[int]
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(19, 6))
    currency: Mapped[str] = mapped_column(String(3), default="CAD")
    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=utc_now_naive,
        server_default=text("CURRENT_TIMESTAMP(6)"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=utc_now_naive,
        onupdate=utc_now_naive,
        server_default=text("CURRENT_TIMESTAMP(6)"),
    )
    product: Mapped[Product] = relationship(back_populates="batches")

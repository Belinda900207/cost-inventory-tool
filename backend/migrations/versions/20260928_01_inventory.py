"""Create products and purchase batches.

Revision ID: 20260928_01_inventory
Revises:
Create Date: 2026-09-28

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision: str = "20260928_01_inventory"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            mysql.DATETIME(fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            mysql.DATETIME(fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "CHAR_LENGTH(normalized_name) > 0", name="ck_products_name_not_empty"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_name"),
    )
    op.create_table(
        "purchase_batches",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("original_quantity", sa.Integer(), nullable=False),
        sa.Column("remaining_quantity", sa.Integer(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=19, scale=6), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("purchased_at", mysql.DATETIME(fsp=6), nullable=False),
        sa.Column(
            "created_at",
            mysql.DATETIME(fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            mysql.DATETIME(fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.CheckConstraint("unit_cost > 0", name="ck_purchase_batches_cost_positive"),
        sa.CheckConstraint("currency = 'CAD'", name="ck_purchase_batches_currency_cad"),
        sa.CheckConstraint(
            "original_quantity > 0", name="ck_purchase_batches_original_positive"
        ),
        sa.CheckConstraint(
            "remaining_quantity >= 0",
            name="ck_purchase_batches_remaining_nonnegative",
        ),
        sa.CheckConstraint(
            "remaining_quantity <= original_quantity",
            name="ck_purchase_batches_remaining_within_original",
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_purchase_batches_product_order",
        "purchase_batches",
        ["product_id", "purchased_at", "id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_purchase_batches_product_order", table_name="purchase_batches")
    op.drop_table("purchase_batches")
    op.drop_table("products")

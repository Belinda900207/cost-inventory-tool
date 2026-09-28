from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.inventory.errors import ProductNameConflict, ProductNotFound
from app.inventory.schemas import PurchaseBatchCreate
from app.inventory.service import InventoryService, normalize_product_name


def test_product_name_is_trimmed_and_casefolded():
    assert normalize_product_name("  Product A  ") == ("Product A", "product a")
    with pytest.raises(ValueError):
        normalize_product_name("   ")


def test_create_product_uses_normalized_name_and_commits():
    repository = MagicMock()
    service = InventoryService(repository)

    product = service.create_product("  Product A  ")

    assert product.name == "Product A"
    assert product.normalized_name == "product a"
    repository.add.assert_called_once_with(product)
    repository.flush.assert_called_once_with()
    repository.commit.assert_called_once_with()


def test_create_product_translates_unique_conflict_and_rolls_back():
    repository = MagicMock()
    repository.flush.side_effect = IntegrityError("insert", {}, Exception("duplicate"))
    service = InventoryService(repository)

    with pytest.raises(ProductNameConflict):
        service.create_product("Product A")

    repository.rollback.assert_called_once_with()
    repository.commit.assert_not_called()


def test_create_batch_requires_existing_product():
    repository = MagicMock()
    repository.get_product.return_value = None
    service = InventoryService(repository)
    request = PurchaseBatchCreate(
        product_id=999,
        quantity=20,
        unit_cost=Decimal("80.000000"),
        currency="CAD",
        purchased_at="2026-09-27T01:00:00Z",
    )

    with pytest.raises(ProductNotFound):
        service.create_purchase_batch(request)

    repository.add.assert_not_called()

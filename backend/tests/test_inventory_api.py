from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.inventory.dependencies import get_inventory_service
from app.inventory.errors import ProductNameConflict
from app.inventory.models import Product, PurchaseBatch
from app.main import create_app


def make_product() -> Product:
    timestamp = datetime(2026, 9, 28, 4, 0, tzinfo=UTC)
    product = Product(
        id=1,
        name="Product A",
        normalized_name="product a",
        created_at=timestamp,
        updated_at=timestamp,
    )
    product.batches = [
        PurchaseBatch(
            id=1,
            product_id=1,
            original_quantity=20,
            remaining_quantity=20,
            unit_cost=Decimal("80.000000"),
            currency="CAD",
            purchased_at=datetime(2026, 9, 27, 1, 0, tzinfo=UTC),
            created_at=timestamp,
            updated_at=timestamp,
        )
    ]
    return product


def test_inventory_routes_return_string_amounts_and_stable_shape():
    product = make_product()
    service = MagicMock()
    service.create_product.return_value = product
    service.list_products.return_value = [product]
    service.create_purchase_batch.return_value = product.batches[0]
    service.list_inventory.return_value = [product]
    service.get_inventory.return_value = product
    app = create_app()
    app.dependency_overrides[get_inventory_service] = lambda: service

    with TestClient(app) as client:
        created = client.post("/api/v1/products", json={"name": " Product A "})
        products = client.get("/api/v1/products")
        batch = client.post(
            "/api/v1/purchase-batches",
            json={
                "product_id": 1,
                "quantity": 20,
                "unit_cost": "80.000000",
                "currency": "CAD",
                "purchased_at": "2026-09-27T01:00:00Z",
            },
        )
        inventory = client.get("/api/v1/inventory/1")

    assert created.status_code == 201
    assert created.json()["name"] == "Product A"
    assert products.json()[0]["product_id"] == 1
    assert batch.status_code == 201
    assert batch.json()["unit_cost"] == "80.00"
    assert inventory.json()["total_remaining_quantity"] == 20
    assert inventory.json()["batches"][0]["unit_cost"] == "80.00"


def test_inventory_validation_and_safe_conflict_error():
    service = MagicMock()
    service.create_product.side_effect = ProductNameConflict
    app = create_app()
    app.dependency_overrides[get_inventory_service] = lambda: service

    with TestClient(app) as client:
        duplicate = client.post("/api/v1/products", json={"name": "PRODUCT A"})
        invalid_currency = client.post(
            "/api/v1/purchase-batches",
            json={
                "product_id": 1,
                "quantity": 20,
                "unit_cost": "80.00",
                "currency": "USD",
                "purchased_at": "2026-09-27T01:00:00Z",
            },
        )
        invalid_quantity = client.post(
            "/api/v1/purchase-batches",
            json={
                "product_id": 1,
                "quantity": 0,
                "unit_cost": "0",
                "currency": "CAD",
                "purchased_at": "2026-09-27T01:00:00Z",
            },
        )

    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "product_name_conflict"
    assert invalid_currency.status_code == 422
    assert invalid_quantity.status_code == 422

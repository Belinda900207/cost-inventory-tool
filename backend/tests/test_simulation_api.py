from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.costing.engine import (
    CostBatch,
    InsufficientInventory,
    calculate_cost_simulation,
)
from app.inventory.errors import ProductNotFound
from app.main import create_app
from app.simulations.dependencies import get_simulation_service
from app.simulations.schemas import display_decimal


def golden_result():
    return calculate_cost_simulation(
        [
            CostBatch(1, 20, Decimal("80"), datetime(2026, 9, 27, tzinfo=UTC)),
            CostBatch(2, 10, Decimal("100"), datetime(2026, 9, 28, tzinfo=UTC)),
        ],
        quantity=25,
        selling_unit_price=Decimal("120"),
    )


def test_display_decimal_uses_round_half_up_only_at_response_boundary():
    assert display_decimal(Decimal("1.005")) == "1.01"
    assert display_decimal(Decimal("86.666666")) == "86.67"


def test_one_item_golden_case_displays_expected_profit_and_margin():
    result = calculate_cost_simulation(
        [
            CostBatch(1, 20, Decimal("80"), datetime(2026, 9, 27, tzinfo=UTC)),
            CostBatch(2, 10, Decimal("100"), datetime(2026, 9, 28, tzinfo=UTC)),
        ],
        quantity=1,
        selling_unit_price=Decimal("120"),
    )

    assert display_decimal(result.fifo.unit_cost) == "80.00"
    assert display_decimal(result.fifo.gross_profit) == "40.00"
    assert display_decimal(result.fifo.gross_margin_percent) == "33.33"
    assert display_decimal(result.weighted_average.unit_cost) == "86.67"
    assert display_decimal(result.weighted_average.gross_profit) == "33.33"
    assert display_decimal(result.weighted_average.gross_margin_percent) == "27.78"


def test_simulation_api_returns_both_methods_as_decimal_strings():
    service = MagicMock()
    service.simulate.return_value = golden_result()
    app = create_app()
    app.dependency_overrides[get_simulation_service] = lambda: service

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/simulations/cost",
            json={
                "product_id": 1,
                "quantity": 25,
                "selling_unit_price": "120.00",
                "currency": "CAD",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "product_id": 1,
        "quantity": 25,
        "currency": "CAD",
        "selling_unit_price": "120.00",
        "revenue": "3000.00",
        "fifo": {
            "method": "fifo",
            "unit_cost": "84.00",
            "total_cost": "2100.00",
            "gross_profit": "900.00",
            "gross_margin_percent": "30.00",
        },
        "weighted_average": {
            "method": "weighted_average",
            "unit_cost": "86.67",
            "total_cost": "2166.67",
            "gross_profit": "833.33",
            "gross_margin_percent": "27.78",
        },
        "difference": {
            "total_cost": {
                "amount": "66.67",
                "higher_method": "weighted_average",
            },
            "gross_profit": {"amount": "66.67", "higher_method": "fifo"},
        },
        "inventory_changed": False,
        "disclaimer": "此結果僅供成本比較，不是正式會計淨利。",
    }


def test_simulation_api_uses_safe_error_envelope():
    service = MagicMock()
    app = create_app()
    app.dependency_overrides[get_simulation_service] = lambda: service

    with TestClient(app) as client:
        service.simulate.side_effect = InsufficientInventory(31, 30)
        insufficient = client.post(
            "/api/v1/simulations/cost",
            json={
                "product_id": 1,
                "quantity": 31,
                "selling_unit_price": "120.00",
                "currency": "CAD",
            },
        )
        service.simulate.side_effect = ProductNotFound
        missing = client.post(
            "/api/v1/simulations/cost",
            json={
                "product_id": 999,
                "quantity": 1,
                "selling_unit_price": "120.00",
                "currency": "CAD",
            },
        )

    assert insufficient.status_code == 409
    assert insufficient.json()["error"]["code"] == "insufficient_inventory"
    assert insufficient.json()["error"]["details"] == {
        "requested": 31,
        "available": 30,
    }
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "product_not_found"


def test_simulation_api_rejects_invalid_inputs():
    service = MagicMock()
    app = create_app()
    app.dependency_overrides[get_simulation_service] = lambda: service
    base = {
        "product_id": 1,
        "quantity": 1,
        "selling_unit_price": "120.00",
        "currency": "CAD",
    }

    with TestClient(app) as client:
        responses = [
            client.post("/api/v1/simulations/cost", json={**base, "quantity": 0}),
            client.post(
                "/api/v1/simulations/cost",
                json={**base, "selling_unit_price": "0"},
            ),
            client.post("/api/v1/simulations/cost", json={**base, "currency": "USD"}),
        ]

    assert [response.status_code for response in responses] == [422, 422, 422]
    service.simulate.assert_not_called()

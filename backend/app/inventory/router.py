from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.inventory.dependencies import get_inventory_service
from app.inventory.errors import ProductNameConflict, ProductNotFound
from app.inventory.models import Product, PurchaseBatch
from app.inventory.schemas import (
    InventoryBatchResponse,
    InventoryResponse,
    ProductCreate,
    ProductResponse,
    PurchaseBatchCreate,
    PurchaseBatchResponse,
)
from app.inventory.service import InventoryService
from app.observability import ApiError

router = APIRouter(prefix="/api/v1", tags=["inventory"])
Service = Annotated[InventoryService, Depends(get_inventory_service)]


def product_response(product: Product) -> ProductResponse:
    return ProductResponse(
        product_id=product.id,
        name=product.name,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


def batch_response(batch: PurchaseBatch) -> PurchaseBatchResponse:
    return PurchaseBatchResponse(
        batch_id=batch.id,
        product_id=batch.product_id,
        original_quantity=batch.original_quantity,
        remaining_quantity=batch.remaining_quantity,
        unit_cost=batch.unit_cost,
        currency=batch.currency,
        purchased_at=batch.purchased_at,
        created_at=batch.created_at,
        updated_at=batch.updated_at,
    )


def inventory_response(product: Product) -> InventoryResponse:
    batches = [
        InventoryBatchResponse(
            batch_id=batch.id,
            original_quantity=batch.original_quantity,
            remaining_quantity=batch.remaining_quantity,
            unit_cost=batch.unit_cost,
            currency=batch.currency,
            purchased_at=batch.purchased_at,
        )
        for batch in product.batches
    ]
    return InventoryResponse(
        product_id=product.id,
        product_name=product.name,
        total_remaining_quantity=sum(item.remaining_quantity for item in batches),
        batches=batches,
    )


@router.post(
    "/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED
)
def create_product(request: ProductCreate, service: Service) -> ProductResponse:
    try:
        return product_response(service.create_product(request.name))
    except ValueError:
        raise ApiError(422, "validation_error", "Invalid request") from None
    except ProductNameConflict:
        raise ApiError(
            409, "product_name_conflict", "Product name already exists"
        ) from None


@router.get("/products", response_model=list[ProductResponse])
def list_products(service: Service) -> list[ProductResponse]:
    return [product_response(product) for product in service.list_products()]


@router.post(
    "/purchase-batches",
    response_model=PurchaseBatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase_batch(
    request: PurchaseBatchCreate, service: Service
) -> PurchaseBatchResponse:
    try:
        return batch_response(service.create_purchase_batch(request))
    except ProductNotFound:
        raise ApiError(404, "product_not_found", "Product not found") from None


@router.get("/inventory", response_model=list[InventoryResponse])
def list_inventory(service: Service) -> list[InventoryResponse]:
    return [inventory_response(product) for product in service.list_inventory()]


@router.get("/inventory/{product_id}", response_model=InventoryResponse)
def get_inventory(product_id: int, service: Service) -> InventoryResponse:
    try:
        return inventory_response(service.get_inventory(product_id))
    except ProductNotFound:
        raise ApiError(404, "product_not_found", "Product not found") from None

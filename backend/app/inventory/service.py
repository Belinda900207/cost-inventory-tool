import unicodedata
from datetime import UTC

from sqlalchemy.exc import IntegrityError

from app.inventory.errors import ProductNameConflict, ProductNotFound
from app.inventory.models import Product, PurchaseBatch
from app.inventory.repository import InventoryRepository
from app.inventory.schemas import PurchaseBatchCreate


def normalize_product_name(value: str) -> tuple[str, str]:
    display_name = value.strip()
    if not display_name:
        raise ValueError("Product name cannot be blank")
    normalized_name = unicodedata.normalize("NFKC", display_name).casefold()
    if len(normalized_name) > 255:
        raise ValueError("Normalized product name is too long")
    return display_name, normalized_name


class InventoryService:
    def __init__(self, repository: InventoryRepository) -> None:
        self.repository = repository

    def create_product(self, name: str) -> Product:
        display_name, normalized_name = normalize_product_name(name)
        product = Product(name=display_name, normalized_name=normalized_name)
        try:
            self.repository.add(product)
            self.repository.flush()
            self.repository.commit()
        except IntegrityError:
            self.repository.rollback()
            raise ProductNameConflict from None
        return product

    def list_products(self) -> list[Product]:
        return self.repository.list_products()

    def create_purchase_batch(self, request: PurchaseBatchCreate) -> PurchaseBatch:
        if self.repository.get_product(request.product_id) is None:
            raise ProductNotFound
        batch = PurchaseBatch(
            product_id=request.product_id,
            original_quantity=request.quantity,
            remaining_quantity=request.quantity,
            unit_cost=request.unit_cost,
            currency=request.currency,
            purchased_at=request.purchased_at.astimezone(UTC).replace(tzinfo=None),
        )
        self.repository.add(batch)
        self.repository.flush()
        self.repository.commit()
        return batch

    def list_inventory(self) -> list[Product]:
        return self.repository.list_inventory()

    def get_inventory(self, product_id: int) -> Product:
        product = self.repository.get_inventory(product_id)
        if product is None:
            raise ProductNotFound
        return product

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.inventory.models import Product, PurchaseBatch


class InventoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: Product | PurchaseBatch) -> None:
        self.session.add(entity)

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def get_product(self, product_id: int) -> Product | None:
        return self.session.get(Product, product_id)

    def list_products(self) -> list[Product]:
        return list(self.session.scalars(select(Product).order_by(Product.id)))

    def list_inventory(self) -> list[Product]:
        statement = (
            select(Product).options(selectinload(Product.batches)).order_by(Product.id)
        )
        return list(self.session.scalars(statement))

    def get_inventory(self, product_id: int) -> Product | None:
        statement = (
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.batches))
        )
        return self.session.scalar(statement)

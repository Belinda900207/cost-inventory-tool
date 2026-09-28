class ProductNameConflict(Exception):
    """A normalized product name already exists."""


class ProductNotFound(Exception):
    """The requested product does not exist."""

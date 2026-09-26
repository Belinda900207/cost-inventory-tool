from collections.abc import Callable
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.config import get_settings

DatabaseCheck = Callable[[], None]


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_timeout=settings.database_timeout,
        connect_args={
            "connect_timeout": settings.database_timeout,
            "read_timeout": settings.database_timeout,
            "write_timeout": settings.database_timeout,
        },
    )


def check_database() -> None:
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))


def get_database_check() -> DatabaseCheck:
    return check_database

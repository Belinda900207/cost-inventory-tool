from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.db import Base
from app.inventory import models as inventory_models


def test_inventory_migration_and_metadata_are_registered():
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    revisions = list(ScriptDirectory.from_config(config).walk_revisions())
    assert [revision.revision for revision in revisions] == ["20260928_01_inventory"]
    assert set(Base.metadata.tables) == {"products", "purchase_batches"}
    assert inventory_models.Product.__tablename__ == "products"
    command.heads(config)

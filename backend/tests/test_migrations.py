from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.db import Base


def test_empty_migration_history_and_no_business_tables():
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    assert list(ScriptDirectory.from_config(config).walk_revisions()) == []
    assert not Base.metadata.tables
    command.heads(config)

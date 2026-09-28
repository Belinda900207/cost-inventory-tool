"""Start an isolated test API without copying or displaying credentials."""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

root = Path(__file__).resolve().parents[1]
values = dotenv_values(root / ".env.test")
if (
    values.get("MYSQL_DATABASE"),
    values.get("MYSQL_USER"),
    values.get("MYSQL_PORT"),
) != ("cost_inventory_test", "test_app", "3307"):
    raise SystemExit("Create the isolated .env.test first; refusing other DB settings")
os.environ.update({key: value for key, value in values.items() if value is not None})
os.chdir(root / "backend")
subprocess.run(
    [sys.executable, "-m", "alembic", "upgrade", "head"],
    check=True,
    timeout=30,
)
os.execv(
    sys.executable,
    [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--no-access-log",
    ],
)

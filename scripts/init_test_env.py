"""Create only the isolated test environment; never overwrite any environment file."""

import os
import secrets
from pathlib import Path

path = Path(__file__).resolve().parents[1] / ".env.test"
content = (
    f"MYSQL_ROOT_PASSWORD={secrets.token_hex(32)}\n"
    f"MYSQL_PASSWORD={secrets.token_hex(32)}\n"
    "MYSQL_DATABASE=cost_inventory_test\nMYSQL_USER=test_app\n"
    "MYSQL_HOST=127.0.0.1\nMYSQL_PORT=3307\n"
)
try:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError:
    print(".env.test already exists; preserved without reading or overwriting.")
else:
    with os.fdopen(fd, "w") as file:
        file.write(content)
    print("Created isolated .env.test (values not displayed).")

"""Initialize a new clone only; preserve every existing .env without reading it."""

import os
import secrets
from pathlib import Path

path = Path(__file__).resolve().parents[1] / ".env"
content = (
    f"MYSQL_ROOT_PASSWORD={secrets.token_hex(32)}\n"
    f"MYSQL_PASSWORD={secrets.token_hex(32)}\n"
    "MYSQL_DATABASE=cost_inventory\nMYSQL_USER=app_user\n"
    "MYSQL_HOST=127.0.0.1\nMYSQL_PORT=3306\n"
    "DATABASE_TIMEOUT=3\n"
)
try:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError:
    print("Existing .env preserved; no values read or changed.")
else:
    with os.fdopen(fd, "w") as file:
        file.write(content)
    print("Created .env with random local credentials; no values displayed.")

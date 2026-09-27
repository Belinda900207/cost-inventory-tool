"""Check tracked artifacts and build output without printing secret values."""

import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
tracked = (
    subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
)
for name in filter(None, tracked):
    path = Path(name)
    if (path.name.startswith(".env") and path.name != ".env.example") or any(
        part
        in {
            "node_modules",
            ".venv",
            "dist",
            "__pycache__",
            "test-results",
            "playwright-report",
        }
        for part in path.parts
    ):
        raise SystemExit(f"Forbidden tracked artifact: {name}")
patterns = [
    rb"gh[pousr]_[A-Za-z0-9]{30,}",
    rb"github_pat_[A-Za-z0-9_]{40,}",
    rb"-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----",
    rb"mysql(?:\+pymysql)?://[^\s]+:[^\s]+@",
]
# Only generated test credentials are read; never inspect the user's development .env.
secrets = []
test_env = root / ".env.test"
if test_env.exists():
    for line in test_env.read_text().splitlines():
        key, _, value = line.partition("=")
        if key.endswith("PASSWORD") and value:
            secrets.append(value.encode())
bundle = root / "frontend/dist"
if not bundle.is_dir():
    raise SystemExit("Build frontend first; no bundle to inspect")
for path in bundle.rglob("*"):
    if path.is_file():
        content = path.read_bytes()
        if any(re.search(pattern, content) for pattern in patterns) or any(
            secret in content for secret in secrets
        ):
            raise SystemExit(f"Potential secret in bundle: {path.relative_to(root)}")
print(
    "Tracked environment/artifact check passed; bundle secret scan passed (heuristic)."
)

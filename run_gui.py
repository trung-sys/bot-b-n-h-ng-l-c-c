from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config.loader import load_settings
from app.runtime import ApplicationRuntime


def main() -> None:
    runtime = ApplicationRuntime(load_settings())
    backup_path = runtime.backup_database()
    print(f"Backup created: {backup_path}")


if __name__ == "__main__":
    main()

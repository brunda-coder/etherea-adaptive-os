#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

HOOK_BODY = """#!/usr/bin/env bash
set -euo pipefail
bash scripts/prevent_binaries.sh
"""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def hook_path() -> Path:
    return repo_root() / ".git" / "hooks" / "pre-commit"


def install() -> None:
    path = hook_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HOOK_BODY, encoding="utf-8")
    path.chmod(0o755)
    print(f"Installed pre-commit hook at {path}")


def uninstall() -> None:
    path = hook_path()
    if path.exists():
        path.unlink()
        print(f"Removed pre-commit hook at {path}")
    else:
        print("No pre-commit hook installed by this helper.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install or remove Etherea git hooks.")
    parser.add_argument("action", choices=["install", "uninstall"], help="Action to perform")
    args = parser.parse_args()

    if args.action == "install":
        install()
    else:
        uninstall()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

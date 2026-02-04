from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_FILES = [
    "etherea.spec",
    "scripts/appimage/Etherea.desktop",
    "scripts/build_linux.sh",
    "scripts/build_windows.ps1",
    "corund/version.py",
    "docs/RELEASE.md",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    missing = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        print("Missing packaging files:", *missing, sep="\n", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

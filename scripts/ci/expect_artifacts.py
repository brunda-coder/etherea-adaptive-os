from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=["windows", "linux", "all"], default="all")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    from corund.version import __version__

    expected = []
    if args.platform in {"windows", "all"}:
        expected.append(root / "dist" / f"Etherea-{__version__}-Windows.exe")
    if args.platform in {"linux", "all"}:
        expected.append(root / f"Etherea-{__version__}-Linux.AppImage")

    missing = []
    small = []
    for path in expected:
        if not path.exists():
            missing.append(str(path))
            continue
        if path.stat().st_size < 10 * 1024 * 1024:
            small.append(str(path))

    if missing:
        print("Missing artifacts:", *missing, sep="\n", file=sys.stderr)
    if small:
        print("Artifacts too small (<10MB):", *small, sep="\n", file=sys.stderr)
    return 1 if missing or small else 0


if __name__ == "__main__":
    raise SystemExit(main())

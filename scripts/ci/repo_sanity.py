from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

FORBIDDEN_DIRS = {"dist", "build", ".venv", "venv", "__pycache__", "node_modules"}
FORBIDDEN_EXTS = {".pyc", ".pyo", ".exe", ".AppImage", ".msi", ".dmg", ".pkg"}


def check_repo_tree(root: Path) -> list[str]:
    violations: list[str] = []
    for base, dirs, files in os.walk(root):
        rel = Path(base).relative_to(root)
        if rel.parts and rel.parts[0] == ".git":
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in {".git"}]
        for d in list(dirs):
            if d in FORBIDDEN_DIRS:
                violations.append(str(rel / d))
        for file in files:
            ext = Path(file).suffix
            if ext in FORBIDDEN_EXTS:
                violations.append(str(rel / file))
    return sorted(set(violations))


def check_tracked_sizes(root: Path) -> list[str]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    violations: list[str] = []
    for raw in output.split(b"\0"):
        if not raw:
            continue
        path = root / raw.decode()
        if not path.exists():
            continue
        if path.stat().st_size > 50 * 1024 * 1024:
            violations.append(str(path.relative_to(root)))
    return violations


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    tree_violations = check_repo_tree(root)
    size_violations = check_tracked_sizes(root)
    if tree_violations:
        print("Forbidden paths present:", *tree_violations, sep="\n", file=sys.stderr)
    if size_violations:
        print("Tracked files >50MB:", *size_violations, sep="\n", file=sys.stderr)
    return 1 if tree_violations or size_violations else 0


if __name__ == "__main__":
    raise SystemExit(main())

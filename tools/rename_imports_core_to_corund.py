"""
Rename import statements from `core` -> `corund` safely-ish.

- Only edits lines that start with `import core` or `from core ...`
- Leaves strings/comments mostly alone (not perfect, but avoids common damage)

Run from repo root:
  python tools/rename_imports_core_to_corund.py

Tip:
  Run `git diff` afterwards and revert anything unexpected.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IMPORT_RE = re.compile(r'^(\s*)(from|import)\s+core(\.|(\s|$))')

def rewrite_file(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False

    changed = False
    out_lines = []
    for line in txt.splitlines(True):
        if IMPORT_RE.match(line):
            if line.lstrip().startswith("from "):
                line = re.sub(r'^(\s*from)\s+core\.', r'\1 corund.', line)
                line = re.sub(r'^(\s*from)\s+core\b', r'\1 corund', line)
            else:
                line = re.sub(r'^(\s*import)\s+core\.', r'\1 corund.', line)
                line = re.sub(r'^(\s*import)\s+core\b', r'\1 corund', line)
            changed = True
        out_lines.append(line)

    if changed:
        p.write_text("".join(out_lines), encoding="utf-8")
    return changed

def main() -> int:
    py_files = list(ROOT.rglob("*.py"))
    changed = 0
    for f in py_files:
        # skip venv / build outputs if present
        if any(part in (".venv", "venv", "build", "dist") for part in f.parts):
            continue
        if rewrite_file(f):
            changed += 1
    print(f"Done. Updated {changed} file(s).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

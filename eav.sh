#!/usr/bin/env bash
set -euo pipefail

# Etherea AutoFix + Validator (EAV) — Mode A (Conservative)
# Auto-fixes env/deps; validates strictly; never rewrites app logic.

# -----------------------
# Helpers
# -----------------------
say() { printf "%s\n" "$*"; }
die() { printf "❌ %s\n" "$*" >&2; exit 1; }

REPO_ROOT="$(pwd)"
export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH:-}"

PY_BIN="${PY_BIN:-python}"

# args
DO_COMMIT=0
DO_PUSH=0
COMMIT_MSG="autofix: stabilize deps & pass checks"

for arg in "$@"; do
  case "$arg" in
    --commit) DO_COMMIT=1 ;;
    --push) DO_PUSH=1 ;;
    --msg=*) COMMIT_MSG="${arg#--msg=}" ;;
    -h|--help)
      say "Usage: ./eav.sh [--commit] [--push] [--msg='message']"
      say "Default: fixes deps, compiles, import-checks, runs tests if available. No commit/push unless asked."
      exit 0
      ;;
    *) die "Unknown arg: $arg (use --help)" ;;
  esac
done

command -v git >/dev/null || die "git not found"
command -v "$PY_BIN" >/dev/null || die "python not found (set PY_BIN=python3 if needed)"

# -----------------------
# 0) Git sanity
# -----------------------
say "🧠 EAV :: starting (Mode A — conservative)"
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  die "Not inside a git repo"
fi

# -----------------------
# 1) Ensure pip works
# -----------------------
say "📦 Ensuring pip…"
"$PY_BIN" -m ensurepip --upgrade >/dev/null 2>&1 || true
"$PY_BIN" -m pip install --upgrade pip >/dev/null 2>&1 || true

# -----------------------
# 2) Install project requirements (best-effort)
# -----------------------
say "📦 Installing requirements (best-effort)…"
REQ_FILES=(
  "requirements-core.txt"
  "requirements-desktop.txt"
  "requirements.txt"
)

for rf in "${REQ_FILES[@]}"; do
  if [ -f "$rf" ]; then
    say "  • pip install -r $rf"
    "$PY_BIN" -m pip install -r "$rf" || true
  fi
done

# Minimal “must-have” libs (common import errors on Termux)
say "📦 Installing core deps (openai, python-dotenv)…"
"$PY_BIN" -m pip install openai python-dotenv >/dev/null 2>&1 || true

# -----------------------
# 3) Create .env if missing (non-destructive)
# -----------------------
if [ ! -f ".env" ]; then
  say "🛠️ Creating empty .env (missing)"
  : > .env
fi

# -----------------------
# 4) Compile all python files (hard gate)
# -----------------------
say "🧪 Syntax compile check…"
"$PY_BIN" - <<'PY'
import pathlib, sys

bad = []
for p in pathlib.Path(".").rglob("*.py"):
    try:
        src = p.read_text(encoding="utf-8")
        compile(src, str(p), "exec")
    except Exception as e:
        bad.append((str(p), str(e)))

if bad:
    print("❌ Syntax errors found (cannot auto-fix safely):")
    for f, e in bad:
        print(f" - {f}: {e}")
    sys.exit(1)

print("✅ Syntax OK")
PY

# -----------------------
# 5) Import checks with auto-install for missing modules
#    Conservative: only auto-install missing module, never edits code.
# -----------------------
say "🔗 Import integrity check (with auto-install for missing modules)…"

"$PY_BIN" - <<'PY'
import os, sys, importlib, subprocess, re

sys.path.append(os.getcwd())

critical = [
    "core.avatar_engine",
    "core.avatar_system",
]

def pip_install(modname: str) -> bool:
    # crude mapping for common cases
    mapping = {
        "dotenv": "python-dotenv",
        "cv2": "opencv-python",
        "PIL": "pillow",
        "sklearn": "scikit-learn",
    }
    pkg = mapping.get(modname, modname)
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        return True
    except Exception:
        return False

for m in critical:
    try:
        importlib.import_module(m)
        print(f"✅ import {m}")
    except ModuleNotFoundError as e:
        missing = e.name
        print(f"⚠️ Missing module '{missing}' while importing {m}. Attempting install…")
        ok = pip_install(missing)
        if not ok:
            print(f"❌ Could not install missing module '{missing}'.")
            raise
        importlib.invalidate_caches()
        importlib.import_module(m)
        print(f"✅ import {m} (after installing {missing})")
    except Exception as e:
        print(f"❌ Runtime/import error in {m}: {e}")
        raise

print("✅ Import checks passed")
PY

# -----------------------
# 6) Run tests if pytest available + tests exist (hard gate if present)
# -----------------------
if [ -d "tests" ] || [ -f "pytest.ini" ]; then
  say "🧪 Tests detected. Attempting to run pytest…"
  if "$PY_BIN" -m pytest -q; then
    say "✅ Tests passed"
  else
    die "Tests failed (won't commit/push)"
  fi
else
  say "ℹ️ No tests detected. Skipping."
fi

# -----------------------
# 7) Clean junk (safe)
# -----------------------
say "🧹 Cleaning caches…"
find . -name "__pycache__" -type d -exec rm -rf {} + >/dev/null 2>&1 || true
find . -name "*.pyc" -delete >/dev/null 2>&1 || true

# -----------------------
# 8) Git status + optional commit/push
# -----------------------
say "📌 Git status:"
git status --short

if [ "$DO_COMMIT" -eq 1 ]; then
  # only commit if there are changes
  if [ -n "$(git status --porcelain)" ]; then
    say "📝 Committing changes…"
    git add -A
    git commit -m "$COMMIT_MSG"
  else
    say "ℹ️ No changes to commit."
  fi
fi

if [ "$DO_PUSH" -eq 1 ]; then
  say "🚀 Pushing to origin…"
  # must be up to date
  git pull --rebase origin main
  git push origin main
  say "✅ Push complete"
else
  say "ℹ️ Push skipped (run with --push to push)."
fi

say "🎉 EAV :: completed successfully"

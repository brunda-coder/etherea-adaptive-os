from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Optional deps we want to tolerate missing on Termux/CI
# (Windows release will install these, so behavior remains intact there)
PATCH_RULES: list[tuple[re.Pattern[str], str]] = []

def add_rule(pattern: str, replacement: str) -> None:
    PATCH_RULES.append((re.compile(pattern), replacement))

# ---- numpy ----
add_rule(
    r"^(import numpy as np)\s*$",
    "try:\n    import numpy as np\nexcept Exception:\n    np = None  # optional on Termux/CI\n",
)

# ---- dotenv ----
add_rule(
    r"^(from dotenv import load_dotenv)\s*$",
    "try:\n    from dotenv import load_dotenv\nexcept Exception:\n    def load_dotenv(*a, **k):\n        return None  # optional on Termux/CI\n",
)

# ---- requests ----
add_rule(
    r"^(import requests)\s*$",
    "try:\n    import requests\nexcept Exception:\n    requests = None  # optional on Termux/CI\n",
)

# ---- openai ----
add_rule(
    r"^(import openai)\s*$",
    "try:\n    import openai\nexcept Exception:\n    openai = None  # optional on Termux/CI\n",
)

# ---- pygame ----
add_rule(
    r"^(import pygame)\s*$",
    "try:\n    import pygame\nexcept Exception:\n    pygame = None  # optional on Termux/CI\n",
)

# ---- speech_recognition ----
add_rule(
    r"^(import speech_recognition as sr)\s*$",
    "try:\n    import speech_recognition as sr\nexcept Exception:\n    sr = None  # optional on Termux/CI\n",
)
add_rule(
    r"^(import speech_recognition)\s*$",
    "try:\n    import speech_recognition\nexcept Exception:\n    speech_recognition = None  # optional on Termux/CI\n",
)

# ---- pyttsx3 ----
add_rule(
    r"^(import pyttsx3)\s*$",
    "try:\n    import pyttsx3\nexcept Exception:\n    pyttsx3 = None  # optional on Termux/CI\n",
)

# ---- pynput (often missing on Termux) ----
add_rule(
    r"^(from pynput import keyboard, mouse)\s*$",
    "try:\n    from pynput import keyboard, mouse\nexcept Exception:\n    keyboard = None\n    mouse = None\n",
)
add_rule(
    r"^(import pynput)\s*$",
    "try:\n    import pynput\nexcept Exception:\n    pynput = None\n",
)

# ---- PySide6: safest minimal stubs for common QtCore + QtWidgets imports ----
# This is intentionally minimal: it prevents import-time crashes on Termux/CI.
# Real UI runs only where PySide6 exists (Windows/Linux desktop).
add_rule(
    r"^(from PySide6\.QtCore import QObject, Signal)\s*$",
    "try:\n    from PySide6.QtCore import QObject, Signal\nexcept Exception:\n    class QObject:  # minimal stub\n        pass\n    def Signal(*a, **k):\n        return None\n",
)
add_rule(
    r"^(from PySide6\.QtCore import QObject, Signal, Slot)\s*$",
    "try:\n    from PySide6.QtCore import QObject, Signal, Slot\nexcept Exception:\n    class QObject:\n        pass\n    def Signal(*a, **k):\n        return None\n    def Slot(*a, **k):\n        def _decorator(fn):\n            return fn\n        return _decorator\n",
)
add_rule(
    r"^(from PySide6\.QtWidgets import QApplication, QWidget)\s*$",
    "try:\n    from PySide6.QtWidgets import QApplication, QWidget\nexcept Exception:\n    QApplication = None\n    class QWidget:\n        pass\n",
)

def looks_already_guarded(s: str, start_idx: int) -> bool:
    # Prevent double-patching if file already has a try/except around the same import nearby.
    window = s[max(0, start_idx-200):start_idx+200]
    return "optional on Termux/CI" in window or "try:\n" in window and "except Exception" in window

def patch_text(text: str) -> tuple[str, int]:
    lines = text.splitlines(True)
    out: list[str] = []
    changed = 0

    for i, ln in enumerate(lines):
        # Only patch top-level imports (no indentation)
        if ln.startswith((" ", "\t")):
            out.append(ln)
            continue

        applied = False
        for rx, rep in PATCH_RULES:
            m = rx.match(ln.rstrip("\n"))
            if m:
                # Skip if already guarded nearby
                if looks_already_guarded(text, text.find(ln)):
                    out.append(ln)
                else:
                    out.append(rep if rep.endswith("\n") else rep + "\n")
                    changed += 1
                applied = True
                break

        if not applied:
            out.append(ln)

    return "".join(out), changed

def main() -> int:
    py_files = [p for p in ROOT.rglob("*.py") if ".git" not in p.parts and "portable" not in p.parts]
    total_changed_files = 0
    total_rewrites = 0

    for p in py_files:
        try:
            s = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        new_s, n = patch_text(s)
        if n and new_s != s:
            p.write_text(new_s, encoding="utf-8")
            total_changed_files += 1
            total_rewrites += n

    print(f"[termux_safety_patch] changed_files={total_changed_files} rewrites={total_rewrites}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

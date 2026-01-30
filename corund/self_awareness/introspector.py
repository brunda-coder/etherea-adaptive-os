from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List


def _repo_root() -> Path:
    """
    Try common layout: run from repo root; else climb from this file.
    Prefer ETHEREA_CORE.md as canonical, but fall back to README.md.
    """
    here = Path(__file__).resolve()
    for up in [here.parent, here.parent.parent, here.parent.parent.parent]:
        if (up / "core").exists() and (
            (up / "ETHEREA_CORE.md").exists() or (up / "README.md").exists()
        ):
            return up
    return Path(os.getcwd()).resolve()


def _count_files(root: Path) -> Dict[str, int]:
    exts: Dict[str, int] = {
        ".py": 0,
        ".md": 0,
        ".png": 0,
        ".json": 0,
        ".yml": 0,
        ".yaml": 0,
        ".txt": 0,
    }
    total = 0
    for p in root.rglob("*"):
        if p.is_file():
            total += 1
            exts[p.suffix.lower()] = exts.get(p.suffix.lower(), 0) + 1
    exts["TOTAL"] = total
    return exts


def build_self_explain_text() -> str:
    """
    Professor-friendly self-explain response.
    No code dumping; describes architecture, how it was built, and how to verify outputs.
    """
    root = _repo_root()
    counts = _count_files(root)

    key = [
        ("UI Shell", "core/ui/main_window_v2.py (Avatar + Aurora + Console + Command Pipeline)"),
        ("Avatar", "core/ui/avatar_heroine_widget.py (emotion-driven heroine renderer)"),
        ("Aurora", "core/ui/aurora_canvas_widget.py + core/aurora_pipeline.py"),
        ("Workspace", "core/workspace_manager.py + core/workspace_ai/* (routing + profiles)"),
        ("Voice", "core/voice_engine.py + core/voice_adapters.py (STT + Edge TTS)"),
        ("Signals", "core/signals.py (Qt signal hub for EI/voice/mode/focus)"),
    ]

    lines: List[str] = []
    lines.append("Etherea — Self Explanation (built-in)")
    lines.append(f"Repo root: {root}")
    lines.append("")

    lines.append("1) What I am")
    lines.append("- A desktop-first living OS prototype: UI + avatar + workspace tooling + voice.")
    lines.append("- My goal is to adapt the interface to human intent and emotional state (EI).")
    lines.append("")

    lines.append("2) How I am built (modules)")
    for title, desc in key:
        lines.append(f"- {title}: {desc}")
    lines.append("")

    lines.append("3) How I make decisions")
    lines.append("- Commands (typed or voice) go into ONE pipeline: route → action → workspace/UI change.")
    lines.append("- Mode changes update avatar persona (calm/focused/strict/soothing) and UI layout.")
    lines.append("")

    lines.append("4) How to verify (demo proofs)")
    lines.append("- Say: 'study mode' / 'coding mode' / 'exam mode' / 'calm mode' and observe layout changes.")
    lines.append("- Say: 'focus 25' and watch focus timer state + avatar enter deep_work persona.")
    lines.append("- Say: 'explain yourself' to see this overview.")
    lines.append("")

    # Canonical doc (preferred)
    core_md = root / "ETHEREA_CORE.md"
    if core_md.exists():
        try:
            doc = core_md.read_text(encoding="utf-8", errors="ignore").strip()
            if doc:
                lines.append("— Canonical Build Doc (ETHEREA_CORE.md) —")
                lines.append(doc)
                lines.append("")
        except Exception:
            pass

    lines.append("5) Build inventory (quick)")
    lines.append(
        f"- Total files: {counts.get('TOTAL', 0)} | Python: {counts.get('.py', 0)} | "
        f"Markdown: {counts.get('.md', 0)} | Assets(PNG): {counts.get('.png', 0)}"
    )

    return "\n".join(lines)

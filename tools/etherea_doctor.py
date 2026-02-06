#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from corund.app_runtime import resolve_asset_path
from corund.capabilities import detect_capabilities


@dataclass
class CheckResult:
    level: str
    name: str
    detail: str
    fix: str = ""


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def _is_venv() -> bool:
    return (
        hasattr(sys, "real_prefix")
        or sys.prefix != getattr(sys, "base_prefix", sys.prefix)
        or bool(getattr(sys, "_base_executable", "") and "venv" in sys.executable.lower())
    )


def _run_checks() -> list[CheckResult]:
    results: list[CheckResult] = []

    version = sys.version_info
    if version >= (3, 10):
        results.append(CheckResult("PASS", "Python version", f"{version.major}.{version.minor}.{version.micro}"))
    else:
        results.append(
            CheckResult(
                "FAIL",
                "Python version",
                f"{version.major}.{version.minor}.{version.micro} (requires >= 3.10)",
                "Install Python 3.10+ and recreate your virtual environment.",
            )
        )

    if _is_venv():
        results.append(CheckResult("PASS", "Virtual environment", f"Active ({sys.prefix})"))
    else:
        results.append(
            CheckResult(
                "WARN",
                "Virtual environment",
                "No active virtual environment detected.",
                "Create one: python -m venv .venv && source .venv/bin/activate (Linux) or .venv\\Scripts\\activate (Windows).",
            )
        )

    critical_modules = {
        "PySide6": "pip install -r requirements-desktop.txt",
        "core": "Run from repo root or fix PYTHONPATH.",
        "corund": "Run from repo root or fix PYTHONPATH.",
    }
    for mod, fix in critical_modules.items():
        if _module_available(mod):
            results.append(CheckResult("PASS", f"Import {mod}", "Available"))
        else:
            results.append(CheckResult("FAIL", f"Import {mod}", "Missing", fix))

    optional_modules = {
        "pygame": "pip install pygame",
        "pyttsx3": "pip install pyttsx3",
        "speech_recognition": "pip install SpeechRecognition",
        "edge_tts": "pip install edge-tts",
        "cv2": "pip install opencv-python",
        "mediapipe": "pip install mediapipe",
    }
    for mod, fix in optional_modules.items():
        if _module_available(mod):
            results.append(CheckResult("PASS", f"Optional {mod}", "Available"))
        else:
            results.append(CheckResult("WARN", f"Optional {mod}", "Not installed", fix))

    caps = detect_capabilities()
    results.append(CheckResult("PASS", "Runtime capabilities", str(caps.to_dict())))

    required_assets = {
        "manifest": "corund/assets/etherea_assets_manifest.json",
        "ui click": "assets/audio/ui_click.wav",
        "ui success": "assets/audio/ui_success.wav",
        "ui whoosh": "assets/audio/ui_whoosh.wav",
        "demo script": "assets/demo/demo_script_01.json",
    }
    for name, key in required_assets.items():
        resolved = resolve_asset_path(key, corund_specific=key.startswith("corund/assets/"))
        if resolved:
            results.append(CheckResult("PASS", f"Asset {name}", resolved))
        else:
            results.append(
                CheckResult(
                    "WARN",
                    f"Asset {name}",
                    f"Not found: {key}",
                    "Verify assets are present or packaged correctly. Non-critical assets can be added later.",
                )
            )

    return results


def main() -> int:
    results = _run_checks()
    has_fail = any(r.level == "FAIL" for r in results)

    print("Etherea Doctor Report")
    print("=" * 22)
    icons = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}
    for r in results:
        line = f"{icons[r.level]} {r.level:<4} | {r.name}: {r.detail}"
        print(line)
        if r.fix:
            print(f"      fix: {r.fix}")

    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for r in results:
        counts[r.level] += 1
    print("-" * 22)
    print(f"Summary: PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}")
    return 1 if has_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

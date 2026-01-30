#!/usr/bin/env python3
"""
Etherea Safe Check ✅
- Never installs anything
- Never crashes even if imports fail
- Works on Termux (Android), Windows, Linux
- Checks: voice, audio, UI, avatar, workspace, assets, packaging readiness
"""

import os
import sys
import traceback
import importlib
from pathlib import Path
from datetime import datetime


OK = "✅"
WARN = "⚠️"
FAIL = "❌"


def _title(msg: str):
    print("\n" + "=" * 70)
    print(msg)
    print("=" * 70)


def _safe_import(mod_name: str):
    try:
        m = importlib.import_module(mod_name)
        return True, m, None
    except Exception as e:
        return False, None, str(e)


def _safe_call(label: str, fn):
    try:
        result = fn()
        print(f"{OK} {label}")
        return True, result
    except Exception as e:
        print(f"{WARN} {label} -> {e}")
        return False, None


def _exists(p: str):
    return Path(p).exists()


def main():
    _title("Etherea Safe Check — Runtime Health Report")

    print(f"🕒 Time: {datetime.now().isoformat(timespec='seconds')}")
    print(f"🧠 Python: {sys.version.split()[0]}")
    print(f"📍 Platform: {sys.platform}")
    print(f"📁 CWD: {os.getcwd()}")

    # ---------------------------
    # 1) BASIC PACKAGE CHECKS
    # ---------------------------
    _title("1) Dependency Presence (No Installation)")

    deps = [
        ("PySide6", "PySide6"),
        ("pygame", "pygame"),
        ("pyttsx3", "pyttsx3"),
        ("speech_recognition", "speech_recognition"),
        ("openai (optional on Termux)", "openai"),
        ("requests", "requests"),
        ("numpy", "numpy"),
    ]

    dep_status = {}
    for label, mod in deps:
        ok, _, err = _safe_import(mod)
        dep_status[mod] = ok
        if ok:
            print(f"{OK} {label} import OK")
        else:
            print(f"{WARN} {label} missing/unavailable -> {err}")

    # ---------------------------
    # 2) PROJECT MODULE CHECKS
    # ---------------------------
    _title("2) Project Modules Import Check")

    modules = [
        "corund.audio_analysis.beat_detector",
        "corund.avatar_motion.dance_planner",

        "corund.avatar_motion.motion_controller",

        "corund.audio_engine",
        "corund.voice_engine",
        "corund.workspace_manager",
        "corund.avatar_system",
        "corund.avatar_engine",
        "corund.emotion_mapper",
        "corund.ui.main_window_v2",
    ]

    mod_ok = {}
    for mod in modules:
        ok, _, err = _safe_import(mod)
        mod_ok[mod] = ok
        if ok:
            print(f"{OK} {mod} import OK")
        else:
            print(f"{FAIL} {mod} import FAILED -> {err}")

    # ---------------------------
    # 3) ASSET CHECKS
    # ---------------------------
    _title("3) Asset Checks (Exists + Pack Ready)")

    assets_to_check = [
        "core/assets/etherea_assets_manifest.json",
        "core/assets/audio/etherea_theme_a.wav",
        "core/assets/animations/splash_pulse.json",
        "core/assets/models/aurora_placeholder.gltf",
        "core/assets/models/aurora_placeholder.bin",
    ]

    for p in assets_to_check:
        if _exists(p):
            print(f"{OK} Found: {p}")
        else:
            print(f"{WARN} Missing: {p}")

    # ---------------------------
    # 4) FEATURE RUNTIME CHECKS (SAFE)
    # ---------------------------
    _title("4) Feature Tests (No Crash Mode)")

    # Audio engine test (only if pygame present + module import OK)
    if mod_ok.get("corund.audio_engine") and dep_status.get("pygame"):
        def _audio_test():
            from corund.audio_engine import AudioEngine
            a = AudioEngine()
            a.set_volume(0.3)
            a.start()
            import time
            time.sleep(1.5)
            a.stop()
            return True

        _safe_call("AudioEngine start/stop (1.5s)", _audio_test)
    else:
        print(f"{WARN} AudioEngine test skipped (missing pygame or audio module)")

    # Voice TTS test (won't fail hard)
    if mod_ok.get("corund.voice_engine") and dep_status.get("pyttsx3"):
        def _tts_test():
            from corund.voice_engine import VoiceEngine
            v = VoiceEngine()
            # If VoiceEngine has speak()
            if hasattr(v, "speak"):
                v.speak("Etherea voice test.")
            return True

        _safe_call("VoiceEngine TTS speak()", _tts_test)
    else:
        print(f"{WARN} Voice TTS test skipped (missing pyttsx3 or voice module)")

    # Workspace test (basic instantiation)
    if mod_ok.get("corund.workspace_manager"):
        def _ws_test():
            from corund.workspace_manager import WorkspaceManager
            w = WorkspaceManager()
            return type(w).__name__

        _safe_call("WorkspaceManager init()", _ws_test)
    else:
        print(f"{WARN} Workspace test skipped (workspace module failed import)")

    # Avatar system basic init (no OpenAI call)
    if mod_ok.get("corund.avatar_system"):
        def _avatar_test():
            from corund.avatar_system import AvatarSystem
            a = AvatarSystem()
            return type(a).__name__

        _safe_call("AvatarSystem init() (no OpenAI call)", _avatar_test)
    else:
        print(f"{WARN} Avatar test skipped (avatar_system import failed)")

    # UI class import test (doesn't launch full GUI)
    if mod_ok.get("corund.ui.main_window_v2") and dep_status.get("PySide6"):
        def _ui_test():
            from corund.ui.main_window_v2 import EthereaMainWindowV2
            return EthereaMainWindowV2.__name__

        _safe_call("UI class available (no window open)", _ui_test)
    else:
        print(f"{WARN} UI test skipped (missing PySide6 or UI import failed)")

    # ---------------------------
    # 5) PACKAGING READINESS CHECK
    # ---------------------------
    _title("5) Packaging Readiness (Release Build)")

    deploy_yml = Path(".github/workflows/release-build.yml")
    if not deploy_yml.exists():
        print(f"{FAIL} release-build.yml missing -> .github/workflows/release-build.yml")
    else:
        txt = deploy_yml.read_text(errors="ignore")
        ok_assets_win = "core/assets;core/assets" in txt
        ok_assets_lin = "core/assets:core/assets" in txt
        print(f"{OK if ok_assets_win else WARN} Windows build bundles assets: {ok_assets_win}")
        print(f"{OK if ok_assets_lin else WARN} Linux build bundles assets: {ok_assets_lin}")

    # ---------------------------
    # 6) FINAL SUMMARY
    # ---------------------------
    _title("6) Summary")

    # core pass criteria: at least UI imports + workspace imports
    core_pass = mod_ok.get("corund.workspace_manager") or mod_ok.get("corund.ui.main_window_v2")

    print(f"{OK if core_pass else WARN} Core system import health: {core_pass}")
    print(f"{OK if dep_status.get('openai') else WARN} OpenAI SDK present locally: {dep_status.get('openai')} (OK to be false on Termux)")
    print(f"{OK} Safe check finished with NO CRASH ✅")

    print("\n📌 Next steps suggestion:")
    print("- If OpenAI is missing on Termux: skip it locally, rely on GitHub Actions builds.")
    print("- Use logs from this check to fix only real failures, not package wars.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(f"{FAIL} Safe Check crashed unexpectedly (should be rare).")
        print(traceback.format_exc())
        sys.exit(1)


# NOTE: Repo uses release-only workflows:
# - .github/workflows/release-tests.yml
# - .github/workflows/release-build.yml

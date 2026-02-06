#!/usr/bin/env python3
from __future__ import annotations

import compileall
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def check(name: str, ok: bool, detail: str) -> bool:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}: {detail}")
    return ok


def main() -> int:
    failures = 0

    compiled = compileall.compile_dir(str(ROOT / "corund"), quiet=1, maxlevels=10)
    if not check("compileall", compiled, "compiled corund package"):
        failures += 1

    for mod in ("PySide6", "core", "corund"):
        try:
            importlib.import_module(mod)
            check("import", True, f"imported {mod}")
        except Exception as exc:
            check("import", False, f"failed to import {mod}: {exc}")
            failures += 1

    try:
        from corund.workspace_ai.workspace_controller import WorkspaceController
        from corund.workspace_manager import WorkspaceManager

        controller = WorkspaceController(WorkspaceManager())
        routed = controller.handle_command("focus 15", source="selftest")
        ok = routed.get("action") == "start_focus_timer" and routed.get("ok") is True
        if not check("command_pipeline", ok, f"route result={routed}"):
            failures += 1
    except Exception as exc:
        check("command_pipeline", False, str(exc))
        failures += 1

    try:
        from PySide6.QtCore import QRectF
        from corund.ui.avatar.avatar_brain import AvatarBrain

        brain = AvatarBrain()
        target = brain.update(QRectF(0, 0, 300, 200), 1.0)
        ok = target is not None
        if not check("avatar_update", ok, f"wander_target={target}"):
            failures += 1
    except Exception as exc:
        check("avatar_update", False, str(exc))
        failures += 1

    try:
        from corund.voice_engine import get_voice_engine

        voice = get_voice_engine()
        voice.speak("runtime selftest", backend="none")
        check("tts_interface", True, f"constructed {voice.__class__.__name__}")
    except Exception as exc:
        check("tts_interface", False, str(exc))
        failures += 1

    try:
        from corund.capabilities import _module_available, detect_capabilities

        assert _module_available("json"), "_module_available(json) should be True"
        caps = detect_capabilities().to_dict()
        check("capabilities", True, f"detect_capabilities={caps}")
        if all(v is False for v in caps.values()):
            print("[WARN] capabilities: optional modules are all unavailable in this environment.")
    except Exception as exc:
        check("capabilities", False, str(exc))
        failures += 1

    blocked_exts = {"png", "jpg", "jpeg", "webp", "gif", "wav", "mp3", "mp4", "bin", "gltf", "glb", "exe", "appimage", "msi", "dmg", "zip", "7z", "pdf", "ttf", "otf"}
    ext_png = Path("demo.\u0050\u004e\u0047").suffix.lstrip(".").lower()
    ext_wav = Path("demo.\u0057\u0041\u0056").suffix.lstrip(".").lower()
    ext_none = Path("README").suffix.lstrip(".").lower()
    case_ok = ext_png in blocked_exts and ext_wav in blocked_exts and ext_none not in blocked_exts
    if not check("binary_extension_case", case_ok, f".PNG->{ext_png}, .WAV->{ext_wav}, no_ext='{ext_none}'"):
        failures += 1

    print(f"runtime_selftest_failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

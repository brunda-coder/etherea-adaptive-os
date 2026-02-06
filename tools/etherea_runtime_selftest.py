#!/usr/bin/env python3
from __future__ import annotations

import compileall
import ctypes.util
import importlib
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def log(status: str, name: str, detail: str) -> bool:
    print(f"[{status}] {name}: {detail}")
    return status == "PASS"


def safe_import(mod: str):
    return importlib.import_module(mod)


def main() -> int:
    failures = 0

    compiled = compileall.compile_dir(str(ROOT), quiet=1, maxlevels=12)
    if not log("PASS" if compiled else "FAIL", "compileall", "python -m compileall ."):
        failures += 1

    for mod in [
        "main",
        "corund.capabilities",
        "corund.voice_engine",
        "corund.os_pipeline",
        "corund.aurora_actions",
        "corund.workspace_ai.router",
        "corund.workspace_ai.workspace_controller",
        "corund.workspace_manager",
        "corund.workspace_ai.session_memory",
        "corund.aurora_adaptation",
        "corund.stress_focus",
        "corund.theme_catalog",
    ]:
        try:
            safe_import(mod)
            log("PASS", "import", mod)
        except Exception as exc:
            failures += 1
            log("FAIL", "import", f"{mod}: {exc}")

    from corund.capabilities import detect_capabilities, selftest_detect_capabilities_guard

    caps = detect_capabilities().to_dict()
    log("PASS", "capabilities", json.dumps(caps, sort_keys=True))
    ok, msg = selftest_detect_capabilities_guard()
    if not log("PASS" if ok else "FAIL", "capabilities_guard", msg):
        failures += 1

    try:
        from corund.voice_engine import VoiceEngine

        engine = VoiceEngine()
        values: list[float] = []
        if hasattr(engine, "viseme_updated") and getattr(engine, "viseme_updated") is not None:
            try:
                engine.viseme_updated.connect(lambda v: values.append(float(v)))
            except Exception:
                pass
        stop = getattr(__import__("threading"), "Event")()
        engine._viseme_pump(0.45, stop)
        smooth = len(values) >= 3 and max(values, default=0.0) > min(values, default=0.0)
        if not log("PASS" if smooth else "FAIL", "speak_test", f"viseme_samples={values[:12]}"):
            failures += 1
        engine.stop()
    except Exception as exc:
        failures += 1
        log("FAIL", "voice_pipeline", str(exc))

    try:
        from corund.app_controller import AppController

        mic_ref = "start_command_loop" in Path(ROOT / "corund/app_controller.py").read_text(encoding="utf-8", errors="ignore")
        if not log("PASS" if mic_ref else "FAIL", "mic_pipeline", "AppController._init_voice_deferred start_command_loop reference"):
            failures += 1
        _ = AppController
    except Exception as exc:
        failures += 1
        log("FAIL", "mic_pipeline", str(exc))

    try:
        from corund.os_pipeline import OSPipeline, OSOverrides
        from corund.os_adapter import OSAdapter

        pipeline = OSPipeline(OSAdapter(dry_run=True))
        result = pipeline.handle_intent("OPEN_URL", {"url": "https://example.com", "confirm": True}, overrides=OSOverrides(kill_switch=True))
        if not log("PASS" if (result.get("reason") == "overrides") else "FAIL", "esc_kill_switch_path", str(result)):
            failures += 1
    except Exception as exc:
        failures += 1
        log("FAIL", "esc_kill_switch_path", str(exc))

    try:
        from corund.workspace_ai.router import WorkspaceAIRouter
        from corund.workspace_ai.workspace_controller import WorkspaceController
        from corund.workspace_manager import WorkspaceManager

        router = WorkspaceAIRouter()
        controller = WorkspaceController(WorkspaceManager())
        suite = ["open workspace", "switch to drawing", "switch to pdf", "switch to coding", "open aurora", "open agent works"]
        routes = [router.route(cmd) for cmd in suite]
        outputs = [controller.handle_command(cmd, source="selftest") for cmd in suite]
        ok = all(r.get("action") != "unknown" for r in routes) and all(isinstance(o, dict) for o in outputs)
        if not log("PASS" if ok else "FAIL", "workspace_voice_switch", f"routes={routes} outputs={outputs}"):
            failures += 1
    except Exception as exc:
        failures += 1
        log("FAIL", "workspace_voice_switch", str(exc))

    try:
        from corund.aurora_actions import ActionRegistry

        registry = ActionRegistry.default()
        action = registry.get("create_presentation") or registry.action_for_intent("create_ppt")
        if not log("PASS" if action is not None else "FAIL", "agent_registry", f"action={getattr(action, 'action_id', None)}"):
            failures += 1
    except Exception as exc:
        failures += 1
        log("FAIL", "agent_registry", str(exc))

    settings_blob = "\n".join(
        Path(p).read_text(encoding="utf-8", errors="ignore")
        for p in [ROOT / "corund/ui/settings_widget.py", ROOT / "corund/ui/settings_privacy_widget.py", ROOT / "web-hero-demo/src/App.tsx"]
        if p.exists()
    ).lower()
    required = ["voice", "mic", "privacy", "retention", "theme", "gradient", "autonomy", "connector"]
    missing = [k for k in required if k not in settings_blob]
    if not log("PASS" if not missing else "FAIL", "settings_schema", f"missing={missing}"):
        failures += 1

    try:
        from corund.theme_catalog import built_in_themes, gradient_creator

        themes = built_in_themes()
        preview = gradient_creator("Custom", "#111", "#333", "#999")
        ok = len(themes) >= 50 and len(preview.stops) == 3
        if not log("PASS" if ok else "FAIL", "themes_gradient", f"themes={len(themes)} preview={preview}"):
            failures += 1
    except Exception as exc:
        failures += 1
        log("FAIL", "themes_gradient", str(exc))

    try:
        from corund.workspace_ai.session_memory import save_snapshot, load_snapshot

        with tempfile.TemporaryDirectory() as td:
            prev = os.getcwd()
            os.chdir(td)
            payload = {"open_files": [{"path": "workspace/doc.txt", "sealed": False}], "retention": "local"}
            out = save_snapshot(payload)
            loaded = load_snapshot()
            os.chdir(prev)
        ok = loaded.get("open_files") == payload.get("open_files") and loaded.get("retention") == "local"
        if not log("PASS" if ok else "FAIL", "memory_persistence", f"saved={out} loaded_keys={list(loaded.keys())}"):
            failures += 1
    except Exception as exc:
        failures += 1
        log("FAIL", "memory_persistence", str(exc))

    if ctypes.util.find_library("GL") is None:
        log("SKIP", "env_libGL", "libGL.so.1 unavailable in this environment")
    else:
        log("PASS", "env_libGL", "libGL detected")

    print(f"SUMMARY failures={failures}")
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

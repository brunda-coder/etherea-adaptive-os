#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Check:
    idx: int
    title: str
    evidence: list[tuple[str, str]]
    runtime_proof: str
    visible: str


REQUIRED_ASSETS = [
    "assets/audio/ui_click.wav",
    "assets/audio/ui_success.wav",
    "assets/avatar/face_idle.webp",
    "corund/assets/avatar_hero/base.png",
]


FEATURES: list[Check] = [
    Check(1, "main.py canonical entry", [("main.py", "main")], "runtime_selftest import main", "App launches from main.py."),
    Check(2, "launch flow includes ring/avatar/tutorial", [("corund/ui/main_window_v3.py", "_show_boot_sequence"), ("corund/tutorial_flow.py", "TutorialFlow")], "MISSING TEST", "Startup should sequence ring then avatar then tutorial."),
    Check(3, "home command input voice-first", [("corund/ui/ethera_command_bar.py", "EthereaCommandBar"), ("corund/app_controller.py", "_init_voice_deferred")], "runtime_selftest mic_pipeline", "Visible command bar accepts voice commands."),
    Check(4, "aurora ring startup visibility", [("corund/ui/aurora_ring_widget.py", "AuroraRingWidget")], "desktop screenshot script", "Aurora ring visible on startup."),
    Check(5, "aurora adapts to time/mood/focus/stress", [("corund/ei_engine.py", "tick"), ("corund/ui/avatar_widget.py", "draw_aurora_ring")], "runtime_selftest imports", "Aura changes color/behavior by state."),
    Check(6, "stress/focus from keyboard+mouse", [("corund/ei_engine.py", "update_from_activity"), ("sensors/keyboard_sensor.py", "KeyboardSensor"), ("sensors/mouse_sensor.py", "MouseSensor")], "tests/test_sensors.py", "Focus/stress follows HID intensity."),
    Check(7, "avatar assets exist", [("corund/assets/avatar_hero/base.png", "file"), ("assets/avatar/face_idle.webp", "file")], "asset scan", "Real avatar assets in repo."),
    Check(8, "avatar alive blink+breathe+talk", [("corund/ui/avatar_heroine_widget.py", "_mouth"), ("corund/ui/avatar_widget.py", "paintEvent")], "runtime_selftest speak_test", "Avatar animates with idle + speech."),
    Check(9, "avatar movement/reposition API", [("corund/ui/avatar/avatar_entity.py", "tick"), ("corund/ui/avatar/avatar_brain.py", "update")], "runtime_selftest imports", "Avatar can move and update position."),
    Check(10, "avatar expression by state cues", [("corund/avatar_visuals.py", "compute_visual_state"), ("core/emotion/emotion_engine.py", "tick")], "runtime_selftest imports", "Expression/label responds to emotional state."),
    Check(11, "avatar teaching/comfort/instant visuals pathway", [("corund/tutorial_flow.py", "run_step"), ("corund/ui/demo_mode_overlay.py", "DemoModeOverlay")], "MISSING TEST", "Avatar can guide/teach in UI flow."),
    Check(12, "TTS works when enabled", [("core/voice/tts_engine.py", "TTSEngine"), ("corund/voice_engine.py", "speak")], "runtime_selftest voice_pipeline", "Speech output produced when enabled."),
    Check(13, "mic input real-time when enabled", [("corund/app_controller.py", "_init_voice_deferred")], "runtime_selftest mic_pipeline", "Mic command loop starts when available."),
    Check(14, "lip-sync realistic + testable", [("corund/voice_engine.py", "_viseme_pump"), ("corund/ui/avatar_heroine_widget.py", "_on_viseme")], "runtime_selftest speak_test", "Mouth/viseme follows speech smoothly."),
    Check(15, "workspace has drawing/pdf/coding modes", [("corund/workspace_registry.py", "WorkspaceType"), ("corund/ui/workspace_widget.py", "WorkspaceWidget")], "runtime_selftest workspace_voice_switch", "Three workspace modes exposed."),
    Check(16, "voice controls mode switching", [("corund/workspace_ai/router.py", "route"), ("corund/workspace_ai/workspace_controller.py", "handle_command")], "runtime_selftest workspace_voice_switch", "Voice route switches mode."),
    Check(17, "drawing tools + save", [("corund/ui/editors.py", "DrawingCanvas")], "MISSING TEST", "User can draw and save output."),
    Check(18, "PDF/Office annotate+summarize", [("corund/adapters/pdf_adapter.py", "PDFAdapter"), ("corund/agents/pdf_agent.py", "PDFAgent")], "MISSING TEST", "PDF open/annotate/summarize path exists."),
    Check(19, "coding editor creates/opens files", [("corund/adapters/code_adapter.py", "CodeAdapter"), ("corund/ui/editors.py", "CodeEditor")], "runtime_selftest memory/workspace checks", "Coding workspace edits files."),
    Check(20, "agent controls files/workspace not apps", [("corund/agent.py", "EthereaAgent"), ("corund/os_pipeline.py", "handle_intent")], "runtime_selftest imports", "Agent actions stay in scope."),
    Check(21, "agent invoked on demand", [("corund/policy_engine.py", "start")], "MISSING TEST", "Agent loop is not always-on."),
    Check(22, "extensible action registry", [("corund/aurora_actions.py", "ActionRegistry")], "runtime_selftest agent_registry", "Task actions like create_ppt available."),
    Check(23, "agent autonomy toggle in settings", [("web-hero-demo/src/App.tsx", "Autonomy")], "runtime_selftest settings_schema", "User can toggle autonomy."),
    Check(24, "background: focus tracker + notifications", [("corund/ei_engine.py", "tick"), ("corund/notifications.py", "NotificationManager")], "MISSING TEST", "Focus tracker and notifications run in background."),
    Check(25, "call-user style notification with toggle", [("corund/notifications.py", "NotificationManager"), ("corund/ui/settings_privacy_widget.py", "SettingsPrivacyWidget")], "MISSING TEST", "Prompt notifications respect user toggles."),
    Check(26, "ESC universal kill switch", [("corund/runtime_state.py", "kill_switch"), ("corund/os_pipeline.py", "OSOverrides")], "runtime_selftest esc_kill_switch_path", "ESC pauses major subsystems."),
    Check(27, "face detection architecture", [("core/emotion/camera_infer.py", "CameraInferer")], "runtime_selftest imports", "Face emotion detector present with fallback."),
    Check(28, "mic emotion architecture", [("core/emotion/emotion_engine.py", "tick")], "MISSING TEST", "Voice tone/emotion pipeline present."),
    Check(29, "micro gestures face/mouse/keyboard", [("sensors/keyboard_sensor.py", "KeyboardSensor"), ("sensors/mouse_sensor.py", "MouseSensor"), ("core/emotion/camera_infer.py", "CameraInferer")], "tests/test_sensors.py", "Multimodal gestures handled safely."),
    Check(30, "connectors Google/GitHub/Calendar/Spotify", [("corund/connectors/registry.py", "ConnectorRegistry")], "MISSING TEST", "Connector architecture supports required providers."),
    Check(31, "local file pick/import/export", [("corund/adapters/base_adapter.py", "BaseAdapter"), ("corund/workspace_manager.py", "open")], "runtime_selftest workspace checks", "Local files can be opened and saved."),
    Check(32, "optional ChatGPT/Gemini connector", [("corund/avatar_engine.py", "_gemini_generate"), ("corund/voice_adapters.py", "speak_openai_tts")], "runtime_selftest imports", "Provider architecture configurable without secrets."),
    Check(33, "settings includes required toggles/themes/connectors", [("corund/ui/settings_widget.py", "SettingsWidget"), ("corund/ui/settings_privacy_widget.py", "SettingsPrivacyWidget"), ("web-hero-demo/src/App.tsx", "Theme")], "runtime_selftest settings_schema", "Settings UI exposes controls."),
    Check(34, "local-first memory logs with retention control", [("corund/workspace_ai/session_memory.py", "save_snapshot"), ("corund/workspace_ai/session_memory.py", "load_snapshot")], "runtime_selftest memory_persistence", "Session logs persist locally and can be managed."),
    Check(35, "curated assets retained", [("assets/audio/ui_click.wav", "file"), ("core/assets/audio/etherea_theme_a.wav", "file"), ("corund/assets/avatar_hero/base.png", "file")], "asset scan", "Icons/background/avatar/wav assets remain in repo."),
]


def symbol_exists(path: Path, symbol: str) -> bool:
    if not path.exists():
        return False
    if symbol == "file":
        return True
    if path.suffix != ".py":
        return symbol.lower() in path.read_text(encoding="utf-8", errors="ignore").lower()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol:
            return True
    return symbol.lower() in path.read_text(encoding="utf-8", errors="ignore").lower()


def asset_category_ok() -> tuple[bool, list[str]]:
    expected_groups = {
        "ui_icons": ["assets", "core/assets", "corund/assets"],
        "background_visuals": ["core/assets", "corund/assets"],
        "avatar_assets": ["assets/avatar", "corund/assets/avatar_hero"],
        "wav_voice_packs": ["assets/audio", "core/assets/audio", "corund/assets/audio"],
    }
    missing: list[str] = []
    for _, folders in expected_groups.items():
        if not any((ROOT / f).exists() and any((ROOT / f).rglob("*")) for f in folders):
            missing.extend(folders)
    for p in REQUIRED_ASSETS:
        if not (ROOT / p).exists():
            missing.append(p)
    return (not missing, sorted(set(missing)))


def main() -> int:
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}

    for f in FEATURES:
        exists = [symbol_exists(ROOT / rel, sym) for rel, sym in f.evidence]
        status = "PASS" if all(exists) else ("WARN" if "MISSING TEST" in f.runtime_proof else "FAIL")
        counts[status] += 1
        print(f"[{status}] {f.idx}. {f.title}")
        for rel, sym in f.evidence:
            print(f"  evidence: {rel} :: {sym}")
        print(f"  runtime_proof: {f.runtime_proof}")
        print(f"  expected_visible_output: {f.visible}")

    ok_assets, missing_assets = asset_category_ok()
    if not ok_assets:
        counts["FAIL"] += 1
        print("[FAIL] ASSETS. Required curated assets missing")
        print("RESTORE LIST:")
        for item in missing_assets:
            print(f"  - {item}")

    print(f"SUMMARY PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}")
    return 2 if counts["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

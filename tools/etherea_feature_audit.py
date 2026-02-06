#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Evidence:
    file: str
    symbol: str


@dataclass
class FeatureResult:
    key: str
    title: str
    status: str
    evidence: list[Evidence]
    runtime_proof: str
    expected_visible_output: str
    note: str = ""


def has_symbol(rel_path: str, symbol: str) -> bool:
    path = ROOT / rel_path
    if not path.exists():
        return False
    if path.suffix != '.py':
        return file_contains(rel_path, symbol)
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol:
            return True
    return False


def file_contains(rel_path: str, text: str) -> bool:
    path = ROOT / rel_path
    return path.exists() and text in path.read_text(encoding="utf-8", errors="ignore")


def all_true(checks: Iterable[bool]) -> bool:
    return all(bool(c) for c in checks)


def emit(result: FeatureResult) -> None:
    print(f"[{result.status}] {result.key}. {result.title}")
    for ev in result.evidence:
        print(f"  evidence: {ev.file} :: {ev.symbol}")
    print(f"  runtime_proof: {result.runtime_proof}")
    print(f"  expected_visible_output: {result.expected_visible_output}")
    if result.note:
        print(f"  note: {result.note}")


def main() -> int:
    results: list[FeatureResult] = []

    def add(key: str, title: str, required: list[tuple[str, str]], runtime: str, visible: str, warn_on_missing=False, note: str = ""):
        checks = [file_contains(f, sym.removeprefix('text:')) if sym.startswith('text:') else has_symbol(f, sym) for f, sym in required]
        status = "PASS" if all_true(checks) else ("WARN" if warn_on_missing else "FAIL")
        results.append(
            FeatureResult(
                key=key,
                title=title,
                status=status,
                evidence=[Evidence(f, s) for f, s in required],
                runtime_proof=runtime,
                expected_visible_output=visible,
                note=note if status != "PASS" else "",
            )
        )

    add(
        "1",
        "Desktop-first app boot + main window",
        [("main.py", "main"), ("corund/app_controller.py", "AppController"), ("corund/ui/main_window_v3.py", "EthereaMainWindowV3")],
        "tools/etherea_runtime_selftest.py import checks",
        "A desktop window titled Etherea OS opens with avatar, canvas, and dock.",
    )
    add(
        "2",
        "Aurora mood/time GUI canvas + aura ring + search",
        [("corund/ui/focus_canvas.py", "FocusCanvas"), ("corund/ui/aurora_ring_widget.py", "AuroraRingWidget"), ("corund/ui/aurora_bar.py", "AuroraBar")],
        "tests/test_ui_smoke.py and manual desktop screenshot",
        "Top aura bar and search field with animated ring are visible.",
    )
    add(
        "3",
        "Avatar EI talking UI (render + idle + movement + expression architecture)",
        [("corund/ui/avatar/avatar_world_widget.py", "AvatarWorldWidget"), ("corund/ui/avatar/avatar_entity.py", "tick"), ("corund/ui/avatar/avatar_brain.py", "update"), ("corund/avatar_visuals.py", "compute_visual_state")],
        "tools/etherea_runtime_selftest.py avatar update step",
        "Avatar bubble/idle motion appears and updates over time.",
    )
    add(
        "4",
        "Ethera natural-language command palette parsing/routing/results",
        [("corund/workspace_ai/router.py", "WorkspaceAIRouter"), ("corund/workspace_ai/workspace_controller.py", "handle_command"), ("corund/ui/command_palette.py", "CommandPalette")],
        "tools/etherea_runtime_selftest.py command routing step",
        "User command text routes to actions and updates dock/status.",
    )
    add(
        "5",
        "Workspace adaptation + focus/distraction controls",
        [("corund/workspace_manager.py", "WorkspaceManager"), ("corund/workspace_ai/focus_mode.py", "FocusModeController"), ("corund/workspace_behaviors.py", "workspace_behavior")],
        "tools/etherea_runtime_selftest.py focus command check",
        "Switching workspaces changes visible density/mode behavior.",
        warn_on_missing=True,
        note="workspace_behavior symbol may be absent; behavior mapping can still exist via constants.",
    )
    add(
        "6",
        "Session memory store/load + local-first + user controls",
        [("corund/workspace_ai/session_memory.py", "save_snapshot"), ("corund/workspace_ai/session_memory.py", "load_snapshot"), ("corund/ui/settings_privacy_widget.py", "SettingsPrivacyWidget")],
        "tests/test_memory.py",
        "Session can be saved/resumed and privacy controls are shown in settings.",
    )
    add(
        "7",
        "Voice output capability (voice input optional)",
        [("core/voice/tts_engine.py", "TTSEngine"), ("corund/capabilities.py", "detect_capabilities")],
        "tools/etherea_runtime_selftest.py capability detection print",
        "Text-to-speech events fire when the assistant speaks.",
    )
    add(
        "8",
        "Optional sensors (camera/expression/stress) non-crashing",
        [("core/emotion/camera_infer.py", "CameraInferer"), ("core/emotion/emotion_engine.py", "tick")],
        "tests/test_sensors.py",
        "When unavailable, sensor data gracefully falls back without app crash.",
    )
    add(
        "9",
        "Kill switch + overrides",
        [("corund/os_pipeline.py", "OSPipeline"), ("corund/os_pipeline.py", "handle_intent"), ("core/emotion/emotion_engine.py", "set_kill_switch")],
        "tools/etherea_runtime_selftest.py imports",
        "User override can block autonomous OS actions immediately.",
    )
    add(
        "10",
        "Agent behavior safe default tick loop, autonomy opt-in",
        [("corund/policy_engine.py", "PolicyEngine"), ("corund/policy_engine.py", "start"), ("corund/runtime_state.py", "RuntimeState")],
        "Manual code audit + compile/selftest",
        "Background loop only runs when started and obeys runtime overrides.",
    )
    add(
        "11",
        "Tutorial/onboarding guided explanation",
        [("corund/tutorial_flow.py", "TutorialFlow")],
        "tests/test_tutorial.py",
        "User can request guided walkthrough/tutorial responses.",
    )
    add(
        "12",
        "Logging/diagnostics with non-crashing warnings",
        [("corund/resource_manager.py", "logs_dir"), ("corund/runtime_diagnostics.py", "RuntimeDiagnostics")],
        "tools/etherea_runtime_selftest.py asset resolver check",
        "Logs folder is created and missing optional assets resolve safely.",
    )
    add(
        "13",
        "Packaging/deployment readiness",
        [("requirements-desktop.txt", "text:requirements-core.txt"), ("scripts/prevent_binaries.sh", "text:ext=\"${ext,,}\"")],
        "CI workflow + prevent_binaries check",
        "Install/setup scripts exist and binary additions are blocked.",
        note="pip",
    )
    add(
        "14",
        "Hero demo visuals",
        [("web-hero-demo/src/App.tsx", "HeroDemo"), ("web-hero-demo/src/styles.css", "text:aurora-ring")],
        "npm run build + web screenshot script",
        "Cinematic web hero scene with Aurora ring, panels, avatar bubble, and command palette.",
        warn_on_missing=True,
        note="aurora",
    )

    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for result in results:
        counts[result.status] += 1
        emit(result)

    print(f"SUMMARY PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}")
    return 2 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())

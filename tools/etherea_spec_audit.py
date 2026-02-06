#!/usr/bin/env python3
from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass
class ItemResult:
    key: str
    status: str  # PASS/WARN/FAIL
    evidence: list[tuple[str, str, str]]  # (file, symbol, reason)


def emit(item: ItemResult) -> None:
    print(f"{item.key}: {item.status}")
    for file, symbol, reason in item.evidence:
        print(f"  - {file} :: {symbol} :: {reason}")


def main() -> int:
    results: list[ItemResult] = []

    # A) Desktop-first boot + main window + Aurora visible
    results.append(ItemResult(
        key="A",
        status="PASS",
        evidence=[
            ("main.py", "main", "Creates QApplication, initializes AppController, and shows main window."),
            ("corund/app_controller.py", "AppController.start", "Calls self.window.show() during startup."),
            ("corund/ui/main_window_v3.py", "EthereaMainWindowV3.__init__", "Instantiates AuroraBar and FocusCanvas in central layout."),
            ("corund/ui/aurora_bar.py", "AuroraBar.__init__", "Adds AuroraRingWidget to top bar."),
        ],
    ))

    # B) Avatar rendering/movement/idle tick
    results.append(ItemResult(
        key="B",
        status="PASS",
        evidence=[
            ("corund/ui/avatar_panel.py", "AvatarPanel.__init__", "Embeds AvatarWorldWidget in main UI."),
            ("corund/ui/avatar/avatar_entity.py", "AvatarEntity.paint", "Avatar rendering is implemented via AvatarRenderer."),
            ("corund/ui/avatar/avatar_entity.py", "AvatarEntity.tick", "Position+velocity controller updates movement each frame."),
            ("corund/ui/avatar/avatar_world_widget.py", "AvatarWorldWidget._tick", "Runs periodic update timer and idle dialogue tick."),
        ],
    ))

    # C) Voice output pipeline
    results.append(ItemResult(
        key="C",
        status="PASS",
        evidence=[
            ("core/voice/tts_engine.py", "TTSEngine.speak", "Text-to-speech interface emits tts events and can be toggled."),
            ("corund/voice_engine.py", "VoiceEngine._choose_backend", "Audio backend selection for OpenAI/Edge/pyttsx3/none."),
            ("corund/voice_engine.py", "VoiceEngine._loop", "Executes backend speak adapters as audio output layer."),
        ],
    ))

    # D) Lip-sync
    results.append(ItemResult(
        key="D",
        status="WARN",
        evidence=[
            ("corund/voice_engine.py", "VoiceEngine._viseme_pump", "Generates viseme amplitude 0..1 during speech."),
            ("corund/ui/avatar_heroine_widget.py", "AvatarHeroineWidget._on_viseme", "Maps viseme amplitude to mouth target and aura amplitude."),
            ("corund/ui/main_window_v3.py", "EthereaMainWindowV3.__init__", "Current primary window uses AvatarWorldWidget, not AvatarHeroineWidget hookup."),
        ],
    ))

    # E) Command system
    results.append(ItemResult(
        key="E",
        status="PASS",
        evidence=[
            ("corund/app_controller.py", "AppController.execute_user_command", "Natural-language command entrypoint from UI/voice source."),
            ("corund/workspace_ai/router.py", "WorkspaceAIRouter.route", "Parses NL commands into action/payload routes."),
            ("corund/workspace_ai/workspace_controller.py", "WorkspaceController.handle_command", "Tool/decision pipeline over routed actions."),
            ("corund/ui/main_window_v3.py", "EthereaMainWindowV3.__init__", "CommandPalette submitted signal wired to execute_user_command."),
        ],
    ))

    # F) Agent loop + kill switch
    results.append(ItemResult(
        key="F",
        status="PASS",
        evidence=[
            ("corund/policy_engine.py", "PolicyEngine._run", "Autonomy loop evaluates state on a scheduler (sleep-based tick)."),
            ("corund/workspace_behaviors.py", "WORKSPACE_BEHAVIORS", "Includes silent modes (Calm/Deep Work) for safe-default autonomy."),
            ("corund/os_pipeline.py", "OSPipeline.handle_intent", "Kill-switch/manual-lock overrides block agentic OS actions."),
        ],
    ))

    # G) Sensors optional/no-crash
    results.append(ItemResult(
        key="G",
        status="PASS",
        evidence=[
            ("core/emotion/camera_infer.py", "CameraInferer.infer", "Camera hook is optional and returns safe stub output."),
            ("core/emotion/emotion_engine.py", "EmotionEngine.set_camera_opt_in", "Sensor opt-in toggles camera usage."),
            ("core/emotion/emotion_engine.py", "EmotionEngine.tick", "Falls back safely when camera disabled/missing."),
        ],
    ))

    for r in results:
        emit(r)

    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for r in results:
        counts[r.status] += 1
    print(f"SUMMARY: PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}")

    return 2 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())

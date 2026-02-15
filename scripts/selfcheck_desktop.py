#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from corund.avatar_engine import AvatarEngine
from corund.workspace_registry import WorkspaceRegistry


BANNED_PHRASES = (
    "as an ai",
    "as a language model",
    "language model",
    "i am an ai",
    "i'm an ai",
)


def fail(message: str) -> int:
    print(f"SELF-CHECK FAIL: {message}")
    return 1


def main() -> int:
    _ = WorkspaceRegistry()
    engine = AvatarEngine()

    probes = ["hello", "EI", "teach regression"]
    for probe in probes:
        raw = engine.speak(probe)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            return fail(f"avatar_engine.speak returned invalid JSON for '{probe}': {exc}")

        for key in ("response", "command", "save_memory", "emotion_update"):
            if key not in payload:
                return fail(f"missing key '{key}' for probe '{probe}'")

        response = str(payload.get("response", "")).lower()
        for phrase in BANNED_PHRASES:
            if phrase in response:
                return fail(f"banned phrase '{phrase}' found in response for '{probe}'")

        emotion_update = payload.get("emotion_update")
        if not isinstance(emotion_update, dict) or not emotion_update:
            return fail(f"emotion_update missing or invalid for '{probe}'")

    print("SELF-CHECK PASS: desktop offline brain contract + phrase hygiene + emotion_update coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

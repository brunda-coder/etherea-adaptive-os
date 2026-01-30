from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from corund.avatar_behavior import AvatarBehaviorEngine
from corund.runtime_state import RuntimeState


def show(label: str, response) -> None:
    print(f"[{label}] text={response.text}")
    print(f"[{label}] lang={response.language_code} speak={response.should_speak}")
    print(f"[{label}] emotion={response.emotion_tag} intensity={response.intensity}")
    print("-")


def main() -> None:
    engine = AvatarBehaviorEngine()
    state = RuntimeState()

    state.current_mode = "focus"
    state.avatar_state = "speaking"
    state.emotion_tag = "bright"
    state.intensity = 0.7

    show("ACTION_SUCCESS", engine.respond("ACTION_FINISHED", state))

    state.overrides.dnd = True
    state.avatar_state = "blocked"
    show("BLOCKED_DND", engine.respond("ACTION_BLOCKED", state))

    state.overrides.dnd = False
    state.avatar_state = "error"
    show("TTS_FAILED", engine.respond("TTS_FAILED", state))

    state.avatar_state = "listening"
    show("KANNADA_INPUT", engine.respond("INTENT_PARSED", state, user_text="ಮುಂದುವರಿಸಲು ವಿವರ ಬೇಕು."))

    show("HINDI_INPUT", engine.respond("INTENT_PARSED", state, user_text="कृपया स्पष्ट करें।"))


if __name__ == "__main__":
    main()

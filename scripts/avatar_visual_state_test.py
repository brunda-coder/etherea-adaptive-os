from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from corund.avatar_visuals import compute_visual_state
from corund.runtime_state import RuntimeState


def show(label: str, state: RuntimeState) -> None:
    visual = compute_visual_state(state)
    print(f"[{label}] {visual}")


def main() -> None:
    state = RuntimeState()
    state.avatar_state = "idle"
    state.emotion_tag = "calm"
    state.intensity = 0.4
    show("idle calm", state)

    state.avatar_state = "listening"
    state.emotion_tag = "curious"
    state.intensity = 0.6
    show("listening curious", state)

    state.avatar_state = "thinking"
    state.emotion_tag = "serious"
    state.intensity = 0.5
    show("thinking serious", state)

    state.avatar_state = "speaking"
    state.emotion_tag = "bright"
    state.intensity = 0.8
    show("speaking bright voice", state)

    state.avatar_state = "speaking"
    state.emotion_tag = "bright"
    state.intensity = 0.8
    state.overrides.dnd = True
    show("speaking bright text", state)

    state.overrides.dnd = True
    state.avatar_state = "blocked"
    state.emotion_tag = "steady"
    state.intensity = 0.3
    show("blocked dnd", state)

    state.overrides.dnd = False
    state.avatar_state = "error"
    state.emotion_tag = "concerned"
    state.intensity = 0.4
    show("error state", state)


if __name__ == "__main__":
    main()

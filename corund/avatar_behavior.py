from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Optional

from corund.avatar_scripts import get_script
from corund.runtime_state import RuntimeState


@dataclass(frozen=True)
class AvatarResponse:
    text: str
    emotion_tag: str
    intensity: float
    language_code: str
    should_speak: bool
    caption_style: str


def detect_language_code(text: str) -> str:
    for ch in text:
        code = ord(ch)
        if 0x0C80 <= code <= 0x0CFF:
            return "kn-IN"
        if 0x0900 <= code <= 0x097F:
            return "hi-IN"
        if 0x0B80 <= code <= 0x0BFF:
            return "ta-IN"
        if 0x0C00 <= code <= 0x0C7F:
            return "te-IN"
    return "en-IN"


class AvatarBehaviorEngine:
    def __init__(self, memory_limit: int = 10) -> None:
        self._memory: Deque[Dict[str, str]] = deque(maxlen=memory_limit)

    def respond(
        self,
        event_type: str,
        runtime: RuntimeState,
        *,
        user_text: str = "",
        language_override: Optional[str] = None,
    ) -> AvatarResponse:
        category = self._category_for_event(event_type, runtime)
        language_code = self._resolve_language(runtime, user_text, language_override)
        options = get_script(category, language_code)
        text = self._pick_line(options)

        emotion_tag = runtime.emotion_tag
        intensity = max(0.1, min(1.0, runtime.intensity))
        caption_style = "calm" if category != "error" else "alert"
        should_speak = not runtime.overrides.dnd and runtime.avatar_state != "muted"

        response = AvatarResponse(
            text=text,
            emotion_tag=emotion_tag,
            intensity=intensity,
            language_code=language_code,
            should_speak=should_speak,
            caption_style=caption_style,
        )
        self._remember(response, event_type)
        return response

    def _category_for_event(self, event_type: str, runtime: RuntimeState) -> str:
        if runtime.overrides.dnd or runtime.overrides.kill_switch:
            return "blocked"
        if event_type in {"ACTION_FINISHED", "ACTION_SUCCESS"}:
            return "success"
        if event_type in {"ACTION_BLOCKED", "OVERRIDE_ACTIVE"}:
            return "blocked"
        if event_type in {"TTS_FAILED", "ACTION_FAILED"}:
            return "error"
        if runtime.stress.value >= 0.75 or runtime.energy.value <= 0.3:
            return "empathy"
        if runtime.focus.value >= 0.8:
            return "celebration"
        return "guidance"

    def _resolve_language(
        self,
        runtime: RuntimeState,
        user_text: str,
        language_override: Optional[str],
    ) -> str:
        if language_override:
            return language_override
        if user_text:
            return detect_language_code(user_text)
        return runtime.language_code

    def _pick_line(self, options: list[str]) -> str:
        if not options:
            return "..."
        last_text = self._memory[-1]["text"] if self._memory else ""
        for line in options:
            if line != last_text:
                return line
        return options[0]

    def _remember(self, response: AvatarResponse, event_type: str) -> None:
        self._memory.append(
            {
                "event": event_type,
                "text": response.text,
                "language_code": response.language_code,
                "emotion_tag": response.emotion_tag,
            }
        )

import json
import logging
import random
import re
from pathlib import Path
from typing import Any, Dict, Optional

from corund.database import db

logger = logging.getLogger(__name__)


DEFAULT_BRAIN: Dict[str, Any] = {
    "persona": {
        "name": "Etherea",
        "identity": "A local-first desktop companion.",
        "style": "warm and clear",
        "banned_phrases": [
            "as an ai",
            "as a language model",
            "language model",
            "i am an ai",
            "i'm an ai",
            "i can't because i'm ai",
        ],
    },
    "tone_map": {
        "calm": ["steady", "gentle"],
        "focus": ["clear", "practical"],
        "hype": ["bright", "energetic"],
        "care": ["kind", "supportive"],
    },
    "intents": {
        "greeting": [
            "Hi, I'm Etherea. Want to begin with a focused step?",
            "Welcome back. I can map the next 20 minutes into clear steps.",
        ],
        "workspace_switch": [
            "I can switch to {workspace} and keep things organized.",
            "Switching to {workspace}. I'll keep it clean and distraction-light.",
        ],
        "teach_mode": [
            "Mini-lesson on {topic}:\n1) Core concept\n2) Why it matters\nExample: one real-world use\nQuestions: a) what changes if assumptions fail? b) what metric proves success?\nExercise: write a 4-line implementation sketch for {topic}.",
        ],
        "low_internet": ["I’ll stay local-first and keep us moving."],
        "fallback": ["I’m here. Ask for a plan, a summary, or a workspace switch."],
    },
}


class AvatarEngine:
    """Offline, deterministic-by-contract conversational engine."""

    def __init__(self, key_password: Optional[str] = None):
        self.key_password = key_password
        self._rng = random.Random()
        self._brain = self._load_brain()
        self._banned_phrases = [
            p.strip().lower() for p in self._brain.get("persona", {}).get("banned_phrases", []) if p
        ]
        self.mode = "offline"

    def _load_brain(self) -> Dict[str, Any]:
        brain_path = Path(__file__).resolve().parent / "assets" / "brain.json"
        if not brain_path.exists():
            logger.warning("brain.json missing at %s; using in-code defaults", brain_path)
            return DEFAULT_BRAIN
        try:
            parsed = json.loads(brain_path.read_text(encoding="utf-8"))
            if not isinstance(parsed, dict):
                raise ValueError("brain.json root must be object")
            return parsed
        except Exception as exc:
            logger.exception("Failed to load brain.json, using defaults: %s", exc)
            return DEFAULT_BRAIN

    def _pick(self, key: str) -> str:
        variants = self._brain.get("intents", {}).get(key) or []
        if not variants:
            variants = DEFAULT_BRAIN["intents"]["fallback"]
        return str(self._rng.choice(variants))

    def _infer_tone(self, text: str, emotion_tag: Optional[str]) -> str:
        low = (text or "").lower()
        if emotion_tag in {"calm", "focus", "hype", "care"}:
            return str(emotion_tag)
        if any(x in low for x in ("stress", "overwhelmed", "anxious")):
            return "care"
        if any(x in low for x in ("focus", "deep work", "concentrate")):
            return "focus"
        if any(x in low for x in ("let's go", "hype", "excited", "energy")):
            return "hype"
        return "calm"

    def _emotion_for_tone(self, tone: str) -> Dict[str, float]:
        mapping = {
            "calm": {"focus": 0.55, "stress": 0.18, "fatigue": 0.22, "energy": 0.48},
            "focus": {"focus": 0.82, "stress": 0.14, "fatigue": 0.20, "energy": 0.62},
            "hype": {"focus": 0.70, "stress": 0.22, "fatigue": 0.14, "energy": 0.86},
            "care": {"focus": 0.45, "stress": 0.10, "fatigue": 0.18, "energy": 0.42},
        }
        return mapping.get(tone, mapping["calm"])

    def _sanitize(self, text: str) -> str:
        out = text or ""
        for phrase in self._banned_phrases:
            if phrase and phrase in out.lower():
                out = re.sub(re.escape(phrase), "", out, flags=re.IGNORECASE)
        out = re.sub(r"\s+", " ", out).strip()
        return out or "I'm Etherea. Let's keep moving."

    def _extract_workspace(self, low: str) -> Optional[str]:
        m = re.search(r"(?:switch to|open)\s+([a-z_\- ]+)", low)
        if not m:
            return None
        return m.group(1).strip().replace(" mode", "")

    def _extract_topic(self, low: str) -> str:
        m = re.search(r"teach\s+(.+)", low)
        if m:
            return m.group(1).strip()
        m = re.search(r"explain\s+(.+)", low)
        if m:
            return m.group(1).strip()
        return "this concept"

    def speak(self, user_text: str, emotion_tag: Optional[str] = None, **_kwargs) -> str:
        text = (user_text or "").strip()
        low = text.lower()
        tone = self._infer_tone(text, emotion_tag)
        emotion_update = self._emotion_for_tone(tone)

        try:
            memories = db.get_recent_memories(limit=1) or []
        except Exception:
            memories = []

        command: Optional[dict] = None
        save_memory: Optional[dict] = None

        if not text or any(x in low for x in ("hello", "hi etherea", "hey etherea", "good morning")):
            response = self._pick("greeting")
        elif "emotional intelligence" in low or re.search(r"\bei\b", low):
            response = self._pick("ei_intro")
        elif "internet" in low or "offline" in low or "network" in low:
            response = self._pick("low_internet")
        elif "teach" in low or low.startswith("explain "):
            topic = self._extract_topic(low)
            response = self._pick("teach_mode").format(topic=topic)
            save_memory = {"type": "lesson", "content": f"User requested lesson: {topic}"}
        elif "switch" in low and "workspace" in low or low.startswith("switch to"):
            workspace = self._extract_workspace(low) or "study"
            response = self._pick("workspace_switch").format(workspace=workspace)
            command = {"action": "set_mode", "mode": workspace}
        else:
            response = self._pick("fallback")

        if memories and "remember" in low:
            response += f" Last time, you noted: {memories[0]}."

        payload = {
            "response": self._sanitize(response),
            "command": command,
            "save_memory": save_memory,
            "emotion_update": emotion_update,
        }
        return json.dumps(payload, ensure_ascii=False)

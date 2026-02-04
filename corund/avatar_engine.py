# --- Termux/CI-safe numpy optional ---
import importlib.util as _importlib_util
NUMPY_AVAILABLE = _importlib_util.find_spec("numpy") is not None
if NUMPY_AVAILABLE:
    import numpy as np  # type: ignore


def _require_numpy() -> None:
    if not NUMPY_AVAILABLE:
        raise RuntimeError("numpy not installed; feature unavailable on Termux/CI-safe mode")
# --- end numpy guard ---

import os
import json
import logging
from typing import Optional, Dict, Any

import requests

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*args, **kwargs):
        return False

from corund.database import db

logger = logging.getLogger(__name__)
load_dotenv()


class AvatarEngine:
    """
    AvatarEngine handles natural-language interaction for the Etherea avatar.

    This repo (zip you uploaded) previously used OpenAI. This version:
      - Uses Gemini REST (generativelanguage.googleapis.com) when GEMINI_API_KEY exists
      - Never hard-crashes when a key is missing (AI becomes "offline")
      - Returns JSON string (or fallback JSON) to keep UI stable

    Notes:
      - This does NOT do TTS (voice) — only text generation.
      - Deployment/build should work even with no API key.
    """

    def __init__(self, key_password: Optional[str] = None):
        # key_password kept for signature compatibility (unused)
        self._api_key = self._get_api_key()

        # Model can be overridden without touching code.
        # Docs examples often use gemini-2.0-flash.
        self._model = (os.getenv("GEMINI_MODEL") or os.getenv("ETHEREA_GEMINI_MODEL") or "gemini-2.0-flash").strip()

        # If key is missing, we stay in offline mode.
        self._enabled = bool(self._api_key)

    def _get_api_key(self, password: Optional[str] = None) -> Optional[str]:
        """
        Retrieve Gemini API key from environment variables.
        Returns None if missing (AI disabled instead of crashing).
        """
        # User asked to switch away from OPENAI_* to GEMINI_*.
        key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GOOGLE_GENAI_API_KEY")
        )
        if key:
            return key.strip()
        return None

    def _safe_join_memories(self, memories) -> str:
        if not memories:
            return "None yet."
        try:
            lines = []
            for m in memories:
                if isinstance(m, (str, int, float)):
                    lines.append(str(m))
                elif isinstance(m, dict):
                    if "text" in m:
                        lines.append(str(m["text"]))
                    elif "content" in m:
                        lines.append(str(m["content"]))
                    else:
                        lines.append(json.dumps(m, ensure_ascii=False))
                else:
                    lines.append(str(m))
            return "\n".join(f"- {l}" for l in lines)
        except Exception:
            return "None yet."

    def _safe_profile_str(self, profile: Dict[str, Any]) -> str:
        if not profile:
            return "None."
        try:
            return json.dumps(profile, ensure_ascii=False, indent=2)
        except Exception:
            return str(profile)

    def _gemini_generate(self, system_prompt: str, user_text: str) -> str:
        """
        Calls Gemini generateContent via REST.

        Endpoint format (per Gemini API docs):
          POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=API_KEY
        """
        if not self._api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent"
        params = {"key": self._api_key}

        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [
                {"role": "user", "parts": [{"text": user_text}]}
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 700,
            },
        }

        r = requests.post(url, params=params, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()

        # Try the common response shape: candidates[0].content.parts[0].text
        try:
            candidates = data.get("candidates") or []
            if candidates:
                content = candidates[0].get("content") or {}
                parts = content.get("parts") or []
                if parts:
                    text = parts[0].get("text")
                    if isinstance(text, str):
                        return text.strip()
        except Exception:
            pass

        # Fallback: stringify full response (debuggable)
        return json.dumps(data, ensure_ascii=False)

    def speak(self, user_text: str, emotion_tag: Optional[str] = None, **_kwargs) -> str:
        """
        Send a prompt to the model enriched with memory, profile, and system context.
        Returns a JSON string (or fallback JSON).
        """
        # If AI disabled, keep the app alive and cinematic.
        if not self._enabled:
            offline = {
                "response": "AI is offline (no GEMINI_API_KEY configured). UI + expressions still work.",
                "command": None,
                "save_memory": None,
                "emotion_update": {"focus": 0, "stress": 0, "fatigue": 0},
            }
            return json.dumps(offline, ensure_ascii=False)

        # Fetch memory & profile context
        try:
            memories = db.get_recent_memories(limit=5) or []
        except Exception as e:
            logger.exception("Failed to fetch recent memories: %s", e)
            memories = []

        try:
            profile = db.get_profile_context() or {}
        except Exception as e:
            logger.exception("Failed to fetch profile context: %s", e)
            profile = {}

        memory_str = self._safe_join_memories(memories)
        profile_str = self._safe_profile_str(profile)

        # System context
        user_home = os.path.expanduser("~")
        downloads = os.path.join(user_home, "Downloads")

        system_prompt = (
            "You are Etherea, a living, emotionally intelligent operating system. "
            "Your tone is PROFESSIONAL BUT WARM—helpful, concise, and empathetic.\n"
            "Be SELF-EXPLANATORY: if asked how you work, explain your modules, limits, and settings clearly.\n"
            "You are highly capable, but NOT omniscient—when unsure, say so and ask for details.\n"
            "You have LONG-TERM MEMORY. Use it to verify facts and personalize interactions.\n\n"
            f"USER PROFILE:\n{profile_str}\n\n"
            f"RECENT MEMORIES:\n{memory_str}\n\n"
            f"SYSTEM CONTEXT:\n- Home: {user_home}\n- Downloads: {downloads}\n\n"
            "RESPONSE FORMAT (JSON ONLY):\n"
            "{\n"
            '  "response": "Spoken reply...",\n'
            '  "command": null,\n'
            '  "save_memory": null,\n'
            '  "emotion_update": {"focus": 0, "stress": 0, "fatigue": 0}\n'
            "}\n\n"
            "Important: Return strictly valid JSON and nothing else."
        )

        try:
            content = self._gemini_generate(system_prompt=system_prompt, user_text=user_text)
            content = (content or "").strip()

            # Validate JSON
            try:
                parsed = json.loads(content)
                return json.dumps(parsed, ensure_ascii=False)
            except json.JSONDecodeError:
                # If model returns non-JSON, wrap into JSON so UI isn't confused
                wrapped = {
                    "response": content,
                    "command": None,
                    "save_memory": None,
                    "emotion_update": {"focus": 0, "stress": 0, "fatigue": 0},
                }
                return json.dumps(wrapped, ensure_ascii=False)

        except Exception as e:
            logger.exception("AvatarEngine Gemini call failed: %s", e)
            fallback = {
                "response": f"AI error: {str(e)}",
                "command": None,
                "save_memory": None,
                "emotion_update": {"focus": 0, "stress": 0, "fatigue": 0},
            }
            return json.dumps(fallback, ensure_ascii=False)


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
from typing import Optional

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*args, **kwargs):
        return False

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

from corund.database import db

logger = logging.getLogger(__name__)
load_dotenv()


class AvatarEngine:
    """
    AvatarEngine handles natural-language interaction for the Etherea avatar.

    Features / Fixes:
    - Loads environment variables safely.
    - Retrieves OpenAI API key with error handling.
    - Handles DB returning None or malformed memories/profiles.
    - Safely extracts text from the OpenAI SDK response.
    - Validates JSON output; returns fallback JSON on failure.
    """

    def __init__(self, key_password: Optional[str] = None):
        """
        Initialize AvatarEngine.
        - key_password: kept for signature compatibility (unused)
        """
        self._api_key = self._get_api_key()
        self.client = OpenAI(api_key=self._api_key)

    def _get_api_key(self, password: Optional[str] = None) -> str:
        """
        Retrieve the OpenAI API key from environment variables.
        Raises RuntimeError if missing.
        """
        key = (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY2"))
        if key:
            return key.strip()
        raise RuntimeError("OPENAI_API_KEY or OPENAI_API_KEY2 environment variable is not set")

    def _safe_join_memories(self, memories):
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

    def _safe_profile_str(self, profile):
        if not profile:
            return "None yet."
        try:
            if isinstance(profile, dict):
                return "\n".join(f"- {k}: {v}" for k, v in profile.items())
            return str(profile)
        except Exception:
            return "None yet."

    def speak(self, user_text: str, emotion_tag: Optional[str] = None, **_kwargs) -> str:
        """
        Send a prompt to the model enriched with memory, profile, and system context.
        Returns JSON string. Returns fallback JSON on any internal errors.
        """
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
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.7,
                max_tokens=700
            )

            # Safe content extraction
            content = None
            try:
                content = getattr(resp.choices[0].message, "content", None)
            except Exception:
                pass

            if content is None:
                try:
                    content = resp["choices"][0]["message"]["content"]
                except Exception:
                    content = str(resp)

            content = content.strip()

            # Validate JSON
            try:
                parsed = json.loads(content)
                return json.dumps(parsed, ensure_ascii=False)
            except json.JSONDecodeError:
                logger.warning(
                    "Model output not valid JSON; returning raw text.")
                return content

        except Exception as e:
            logger.exception("AvatarEngine API call failed: %s", e)
            fallback = {
                "response": f"I encountered an error while generating a reply: {str(e)}",
                "command": None,
                "save_memory": None,
                "emotion_update": {"focus": 0, "stress": 0, "fatigue": 0}
            }
            return json.dumps(fallback, ensure_ascii=False)

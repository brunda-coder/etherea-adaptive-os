"""
Avatar System for Etherea (Foundation)
- Multiple avatar profiles + dynamic switching
- Costume + background/environment switching
- Expressive actions: dance/sing/surprise
- Safe style imitation mode (no copyrighted imitation)
- Emotion-aware presence linked with system state
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
import time
import random
import os
import json

from corund.emotion_mapper import EmotionMapper
from corund.resource_manager import ResourceManager

@dataclass
class AvatarProfile:
    id: str
    name: str
    costume: str = "default"
    background: str = "workspace"
    safe_style_mode: str = "neutral"   # safe imitation mode descriptor
    meta: Dict[str, Any] = field(default_factory=dict)

class AvatarSystem:
    def __init__(self):
        self.mapper = EmotionMapper()
        self.profiles: Dict[str, AvatarProfile] = {}
        self.active_id: Optional[str] = None

        # EI-like state (0..1)
        self.emotion = {"focus": 0.5, "stress": 0.2, "energy": 0.5, "curiosity": 0.5}
        self.last_action = None

        # load manifest and language/task metadata
        self.manifest = self._load_manifest()
        # supported languages for communication (e.g. English, Hindi, Kannada, Tamil, Telugu)
        self.supported_languages: List[str] = self.manifest.get("supported_languages", [])
        # Long-term task plan for Etherea development
        self.task_plan: List[str] = self.manifest.get("task_plan", [])
        self.current_task_index: int = 0

        # create default avatar
        self.create_profile("aurora", "Aurora")

    # -------- Profiles --------
    def create_profile(self, profile_id: str, name: str, **kwargs) -> AvatarProfile:
        p = AvatarProfile(id=profile_id, name=name, **kwargs)
        self.profiles[profile_id] = p
        if self.active_id is None:
            self.active_id = profile_id
        return p

    def switch_profile(self, profile_id: str) -> bool:
        if profile_id in self.profiles:
            self.active_id = profile_id
            return True
        return False

    def get_active(self) -> AvatarProfile:
        if not self.active_id:
            raise RuntimeError("No active avatar profile.")
        return self.profiles[self.active_id]

    # -------- Costume / Background --------
    def set_costume(self, costume: str):
        self.get_active().costume = costume

    def set_background(self, bg: str):
        self.get_active().background = bg

    def set_safe_style_mode(self, mode: str):
        # safe mode only stores a descriptor (no imitation of copyrighted characters)
        self.get_active().safe_style_mode = mode

    # -------- Expressive Actions --------
    def do_action(self, action: str) -> str:
        action = action.lower().strip()
        self.last_action = action

        if action in ("dance", "dancing"):
            return f"💃 {self.get_active().name} is dancing with cosmic energy!"
        if action in ("sing", "singing"):
            return f"🎶 {self.get_active().name} is humming a safe original melody."
        if action in ("surprise", "wow", "shock"):
            # Cinematic surprise: produce a flourish with a magical vibe
            return f"🎬 {self.get_active().name} conjures a cinematic surprise, shimmering with stardust!"
        return f"✨ {self.get_active().name} performed: {action}"

    # -------- Emotion Updates --------
    def update_emotion(self, **updates):
        for k, v in updates.items():
            if k in self.emotion:
                try:
                    f = float(v)
                except Exception:
                    continue
                self.emotion[k] = max(0.0, min(1.0, f))

    def get_visual_state(self) -> Dict[str, float]:
        return self.mapper.update(self.emotion)

    # -------- GUI Compatibility Methods --------
    def get_current_ei_state(self):
        # Aurora GUI expects either str or dict
        focus = self.emotion.get("focus", 0.5)
        stress = self.emotion.get("stress", 0.2)
        if stress > 0.7:
            return "Stressed"
        if focus > 0.7:
            return "Focused"
        return "Neutral"

    def get_visual_for_response(self, response: str) -> str:
        # simple icon feedback
        icons = ["💡 Idea Spark", "🔥 Focus Flame", "🌙 Calm Aura", "⚡ Energy Pulse", "✨ Glow Shift"]
        if "error" in response.lower():
            return "🚨 Alert"
        return random.choice(icons)

    def generate_response(self, user_text: str) -> str:
        """
        Generate a textual response for the avatar given the user input. Supports
        simple emotion updates, action hints, language prefixes for
        multilingual acknowledgement, and post‑processing to avoid
        disempowering phrases. Later versions may connect this to AvatarEngine
        or other large language models.
        """

        # Detect language prefix (e.g. "Hindi: hello") and strip it from user_text
        language: Optional[str] = None
        lowered = user_text.lower().strip()
        prefixes: Dict[str, str] = {
            "hindi:": "Hindi",
            "kannada:": "Kannada",
            "tamil:": "Tamil",
            "telugu:": "Telugu",
        }
        for pref, lang in prefixes.items():
            if lowered.startswith(pref):
                language = lang
                # remove prefix from the original user_text preserving case
                user_text = user_text[len(pref):].strip()
                break

        active = self.get_active()
        mood = self.get_current_ei_state()
        style = active.safe_style_mode
        bg = active.background
        costume = active.costume

        # lightweight behavior: update focus/stress based on keywords
        t = user_text.lower()
        if "focus" in t:
            self.update_emotion(focus=min(1.0, self.emotion["focus"] + 0.1))
        if "stress" in t or "tired" in t:
            self.update_emotion(stress=min(1.0, self.emotion["stress"] + 0.1))

        action_hint = ""
        if any(w in t for w in ["dance", "sing", "surprise"]):
            for w in ["dance", "sing", "surprise"]:
                if w in t:
                    action_hint = self.do_action(w)
                    break

        response = (
            f"{active.name} [{mood}] ({style}) 🌌\n"
            f"🎭 Costume: {costume} | 🌄 Background: {bg}\n"
            f"🗣️ {active.name}: I understood → {user_text}\n"
            f"{action_hint}"
        )
        # Avoid saying "can't" unless truly impossible/unethical
        response = self._avoid_cant(response)
        # Apply simple language acknowledgement if a prefix was detected
        if language:
            response = self._apply_language_ack(response, language)
        return response

    # -------- Manifest / Introspection --------
    def _load_manifest(self) -> Dict[str, Any]:
        """
        Load avatar manifest containing style, language support and task plan.
        If the manifest does not exist, create a default one. The manifest
        enables the avatar to be introspective about its design choices and
        long‑term goals. Information from this file can be surfaced to
        downstream engines (e.g. AvatarEngine) for self‑awareness and
        planning.
        """
        manifest_path = ResourceManager.resolve_asset("core/assets/avatar_manifest.json", corund_specific=True)

        # default manifest values
        default_manifest = {
            "style": "high-res 3D soft disney non-human non-anime",
            "supported_languages": ["English", "Hindi", "Kannada", "Tamil", "Telugu"],
            "task_plan": [
                "Set up the database",
                "Implement the AI avatar core",
                "Integrate emotional intelligence (EI) signals",
                "Add high resolution 3D visuals for the avatar",
                "Enable multilingual support (Hindi, Kannada, Tamil, Telugu)",
                "Create cinematic surprise interactions",
                "Refine persona to avoid saying 'can't' except when unethical",
                "Develop step‑by‑step task planning and tracking system"
            ]
        }

        # Attempt to load an existing manifest
        try:
            if manifest_path and os.path.exists(manifest_path):
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data
        except Exception:
            # corrupt file or parse error will fall back to default
            pass

        return default_manifest

    # -------- Task Plan Utilities --------
    def get_next_task(self) -> Optional[str]:
        """
        Retrieve the next planned task from the task plan. Once all tasks
        have been served, returns None. Consumers may reset
        self.current_task_index to start over or modify task_plan if needed.
        """
        if not self.task_plan:
            return None
        if self.current_task_index >= len(self.task_plan):
            return None
        task = self.task_plan[self.current_task_index]
        self.current_task_index += 1
        return task

    # -------- Response Post-processing --------
    def _avoid_cant(self, text: str) -> str:
        """
        Replace occurrences of "can't" with a more empowering phrase unless
        the statement clearly relates to ethical or impossible situations.
        This helps the avatar maintain a positive tone while still
        communicating boundaries when necessary.
        """
        # Simple replacement: avoid contractions of cannot
        return text.replace(" can't", " will try to").replace("Can't", "Will try to")

    def _apply_language_ack(self, text: str, language: str) -> str:
        """
        Prepend a simple acknowledgement in the requested language. This is a
        placeholder illustrating multilingual capability; full translation
        should be implemented by connecting to proper translation services.

        :param text: The original response text.
        :param language: The language name (e.g. "Hindi", "Kannada").
        :return: Modified text with a language‑specific greeting.
        """
        greetings = {
            "Hindi": "नमस्ते! मैंने समझा.",
            "Kannada": "ನಮಸ್ಕಾರ! ನಾನು ಅರ್ಥ ಮಾಡಿಕೊಳ್ಳಿದ್ದೇನೆ.",
            "Tamil": "வணக்கம்! நான் புரிந்துகொண்டேன்.",
            "Telugu": "నమస్తే! నేను అర్ధం చేసుకున్నాను.",
        }
        greeting = greetings.get(language, "")
        if greeting:
            return f"{greeting}\n{text}"
        return text

import time
import threading
import logging
import math
from typing import Dict
from corund.signals import signals

logger = logging.getLogger("etherea_internal")
logger.setLevel(logging.WARNING)


class EIEngine:
    def __init__(self):
        self.emotion_vector: Dict[str, float] = {
            "focus": 0.5,
            "stress": 0.2,
            "energy": 0.5,
            "curiosity": 0.5,
            "flow": 0.0,
        }
        self.state = self.emotion_vector
        self.sub_states: Dict[str, float] = {
            "flow_intensity": 0.0,
            "typing_rhythm": 0.5,
            "physical_jitter": 0.0,
        }
        self.last_update = time.time()
        self.running = False
        self._lock = threading.Lock()
        self._thread = None
        self._stop_event = threading.Event()
        self.last_proactive_trigger = 0.0
        self.trigger_cooldown = 120.0

        # Persistence throttling
        self.last_save_time = 0.0
        self.save_interval = 30.0
        self.last_saved_stress = 0.0

        try:
            if hasattr(signals, "input_activity"):
                signals.input_activity.connect(self.on_input_activity)
            if hasattr(signals, "pattern_detected"):
                signals.pattern_detected.connect(self.on_pattern_detected)
        except Exception:
            pass

    def _clamp(self, value: float) -> float:
        try:
            if math.isnan(value) or math.isinf(value):
                return 0.5
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.5

    def on_input_activity(self, activity_type: str, payload):
        with self._lock:
            intensity = 0.0
            jitter = 0.0
            variance = 0.0
            if isinstance(payload, dict):
                intensity = payload.get("intensity", 0.0)
                jitter = payload.get("jitter", 0.0)
                variance = payload.get("variance", 0.0)
            else:
                intensity = payload

            intensity = self._clamp(intensity)
            jitter = self._clamp(jitter)
            variance = self._clamp(variance)

            if activity_type == "typing":
                self.emotion_vector["focus"] += 0.05 * intensity
                self.emotion_vector["energy"] -= 0.01 * intensity
                if intensity > 0.8:
                    self.emotion_vector["stress"] += 0.02
                self.sub_states["typing_rhythm"] = self._clamp(1.0 - variance)
            elif activity_type == "mouse":
                self.emotion_vector["curiosity"] += 0.02 * intensity
                if intensity > 0.9:
                    self.emotion_vector["stress"] += 0.05
                    self.emotion_vector["focus"] -= 0.02
                if jitter > 0.0:
                    self.sub_states["physical_jitter"] = max(
                        self.sub_states["physical_jitter"], jitter)
                    if jitter > 0.5:
                        self.emotion_vector["stress"] += 0.03 * jitter

            if self.sub_states["typing_rhythm"] > 0.7 and self.emotion_vector["stress"] < 0.5:
                self.sub_states["flow_intensity"] = self._clamp(
                    self.sub_states["flow_intensity"] + 0.02 * intensity)
                self.emotion_vector["flow"] = self.sub_states["flow_intensity"]

            for k in self.emotion_vector:
                self.emotion_vector[k] = self._clamp(self.emotion_vector[k])

    def start(self):
        if self.running:
            return
        self.running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(1.0)

    def _loop(self):
        while not self._stop_event.is_set():
            now = time.time()
            dt = max(0.0, min(now - self.last_update, 1.0))
            self.last_update = now
            with self._lock:
                self.emotion_vector["stress"] -= 0.05 * dt
                self.emotion_vector["focus"] -= 0.02 * dt
                self.emotion_vector["energy"] += 0.01 * dt
                self.sub_states["flow_intensity"] = self._clamp(
                    self.sub_states["flow_intensity"] - 0.01 * dt)
                self.emotion_vector["flow"] = self.sub_states["flow_intensity"]

                if self.emotion_vector["focus"] > 0.8:
                    self.emotion_vector["stress"] *= 0.9
                    if self.emotion_vector["stress"] < 0.1:
                        self.emotion_vector["stress"] = 0.0

                for k in self.emotion_vector:
                    self.emotion_vector[k] = self._clamp(self.emotion_vector[k])

                try:
                    current_stress = self.emotion_vector["stress"]
                    stress_diff = abs(current_stress - self.last_saved_stress)
                    if (now - self.last_save_time > self.save_interval) or (stress_diff > 0.15):
                        from corund.database import db

                        db.set_preference("last_emotion", str(self.emotion_vector))
                        self.last_save_time = now
                        self.last_saved_stress = current_stress

                    signals.emotion_updated.emit(self.emotion_vector.copy())
                except Exception:
                    pass

                self._check_triggers(now)
            time.sleep(0.05)

    def on_pattern_detected(self, patterns: dict):
        with self._lock:
            hesitation = patterns.get("hesitation", False)
            repetition = patterns.get("repetition", False)
            late_night = patterns.get("late_night", False)
            deletions = patterns.get("deletions", 0)

            # 1. Micro-Hesitation & Uncertainty (Deletions)
            if deletions > 2:
                # Interpret as uncertainty/perfectionism -> Mirror with structured clarity
                self.emotion_vector["stress"] = self._clamp(self.emotion_vector["stress"] + 0.03 * deletions)
                self.emotion_vector["curiosity"] = self._clamp(self.emotion_vector["curiosity"] + 0.05)
            
            # 2. Confidence Matching / Repetition
            if repetition:
                # User is stuck or looping: increase stress baseline subtly
                self.emotion_vector["stress"] = self._clamp(self.emotion_vector["stress"] + 0.05)
                # Mirror overwhelmed state -> remove pressure
                self.emotion_vector["energy"] *= 0.8
            
            # 3. Silence / Idle Hesitation
            if hesitation and self.emotion_vector["focus"] > 0.6:
                # User is paused/thinking: increase curiosity
                self.emotion_vector["curiosity"] = self._clamp(self.emotion_vector["curiosity"] + 0.1)
                self.emotion_vector["energy"] *= 0.9 # Slow down presence
            
            # 4. Implicit Emotional Safety Net (Late Night/Overwhelmed)
            if late_night:
                # Dampen energy and stress for a calmer night experience
                self.emotion_vector["energy"] *= 0.8
                self.emotion_vector["stress"] *= 0.7
            
            # Normalize state without advice (Manifest Rule)
            for k in self.emotion_vector:
                self.emotion_vector[k] = self._clamp(self.emotion_vector[k])

    def _check_triggers(self, now):
        if now - self.last_proactive_trigger < self.trigger_cooldown:
            return
        if self.emotion_vector["stress"] > 0.85:
            signals.proactive_trigger.emit("stress_relief")
            self.last_proactive_trigger = now
        elif self.emotion_vector["focus"] > 0.9:
            signals.proactive_trigger.emit("focus_shield_active")
            self.last_proactive_trigger = now

from __future__ import annotations

try:
    from PySide6.QtCore import QObject, Signal
except Exception:
    class QObject:  # minimal stub
        pass
    def Signal(*a, **k):
        return None


class EISignals(QObject):
    """
    Central Qt signal hub.

    Backwards compatible:
      - keeps existing signals used across the repo
      - adds voice + focus + mode + TTS lifecycle signals for the final demo pipeline
    """

    # --- existing (keep) ---
    input_activity = Signal(str, object)  # allow dict payloads
    emotion_updated = Signal(dict)
    visual_action_triggered = Signal(str)
    proactive_trigger = Signal(str)
    command_received = Signal(str)
    avatar_state_change = Signal(str)
    system_log = Signal(str)
    command_received = Signal(str)  # legacy: generic command text
    avatar_state_change = Signal(str)
    pattern_detected = Signal(dict)
    system_log = Signal(str)

    # --- new: voice / command pipeline ---
    command_received_ex = Signal(str, dict)  # (text, meta) meta: {"source": "...", ...}
    voice_transcript = Signal(str, dict)     # (text, meta)
    voice_state = Signal(str, dict)          # LISTENING / THINKING / IDLE / ERROR

    # --- new: workspace modes / focus timer ---
    mode_changed = Signal(str, dict)         # (mode, meta)
    focus_started = Signal(int, dict)        # (minutes, meta)
    focus_stopped = Signal(dict)             # meta
    focus_tick = Signal(int, dict)           # (seconds_left, meta)

    # --- new: TTS lifecycle (for UI + avatar mouth) ---
    tts_requested = Signal(str, dict)        # (text, meta)
    tts_started = Signal(str, dict)          # (text, meta)
    tts_finished = Signal(str, dict)         # (text, meta)
    tts_failed = Signal(str, dict)           # (text, meta)


signals = EISignals()

> 🟡 **CONCEPT / DESIGN DOC**
> This file may describe a broader or planned model. For the **current working demo behavior and commands**, see **ETHEREA_CORE.md**.

**Current implemented demo modes** (as of this build): `study`, `coding`, `exam`, `calm`, plus focus-session `deep_work` persona.

# Runtime State Model (Single Source of Truth)

The runtime state is a single object that other subsystems read from and update. It is used to derive Aurora and avatar visuals without UI-side execution.

## Core fields (implemented)
- **focus/stress/energy**: metric values with `{value, source, timestamp}`.
- **current_mode**: `idle | focus | break | study | coding`.
- **last_intent**: last resolved intent string (if available).
- **avatar_state**: `idle | listening | thinking | speaking | blocked | error | muted`.
- **emotion_tag + intensity**: current emotional tone and intensity.
- **audio_state**: background audio + TTS active flags.
- **overrides**: `kill_switch | dnd | manual_lock | privacy_mode`.
- **workspace_state**: active workspace id/name, session info, last saved time.
- **visual_settings**: `reduce_motion` and intensity preset.
- **language_code**: `en-IN | hi-IN | kn-IN | ta-IN | te-IN`.

## Reference implementation
See `core/runtime_state.py` for the canonical data model and helper methods.

## Notes
- AuroraCanvasState is derived from runtime state + action registry (see `core/aurora_state.py`).
- Override flags immediately block adaptive actions and mute TTS if DND is active.
# Etherea Minimal State Model

## Purpose
Document the core runtime state in a minimal, implementation-aligned schema. This is documentation only.

## State Schema (Conceptual)
```json
{
  "runtime": {
    "app_mode": "desktop",
    "version": "optional",
    "uptime_s": 0
  },
  "workspace": {
    "mode": "study|coding|exam|calm|unknown",
    "session": {
      "has_saved_session": false,
      "last_session_id": "optional"
    },
    "last_command": "optional"
  },
  "ei": {
    "focus": 0.0,
    "stress": 0.0,
    "energy": 0.0,
    "curiosity": 0.0
  },
  "ui": {
    "theme": "dark|light",
    "accent": "violet|cyan",
    "avatar_state": "idle|thinking|listening"
  },
  "audio": {
    "background_enabled": true,
    "voice_enabled": true,
    "is_playing": false
  },
  "overrides": {
    "kill_switch": false,
    "audio_enabled": true,
    "voice_enabled": true,
    "sensors_enabled": true,
    "reason": "optional"
  },
  "sensors": {
    "enabled": false,
    "last_input_kind": "optional"
  }
}
```

## Ownership Notes
- **workspace**: owned by `core/workspace_manager.py` and `core/workspace_ai/*`.
- **ei**: owned by `core/ei_engine.py` and updated via `core/signals.py`.
- **ui**: owned by `core/ui/*` widgets.
- **audio/voice**: owned by `core/audio_engine.py` and `core/voice_engine.py`.
- **sensors**: owned by `sensors/*` modules.
- **overrides**: owned by runtime policy (documented; intended to be honored across subsystems).

## Constraints
- Desktop-first remains the primary mode.
- Voice and background audio support remain enabled (optional dependencies may be missing at runtime).
- Advanced avatar animation remains deferred.
- Overrides/kill-switches are policy-only here; implementation remains unchanged.

# Avatar Visual System

The avatar’s visual layer is derived from runtime state to avoid UI-only logic. It is deterministic and respects `reduce_motion`.

## VisualState fields
- `glow_level` (0–1)
- `pulse_speed`
- `breath_rate`
- `eye_blink_rate`
- `idle_sway_amp`
- `speaking_bob_amp`
- `thinking_orbit_speed`
- `blocked_dim_level`
- `error_flicker`
- `caption_style` (`calm | alert | celebrate`)

## Mapping summary
- **avatar_state** controls base motion (idle/listening/thinking/speaking/blocked/error/muted).
- **emotion_tag** overlays tone (bright/proud/curious/steady/serious/apologetic/concerned).
- **intensity** scales amplitude with safe clamping.
- **reduce_motion** clamps sway/bob/orbit to low-motion ranges.

Reference implementation: `core/avatar_visuals.py`.

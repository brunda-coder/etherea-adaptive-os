# ETHEREA UI Spec — Vivid Soul

## Identity
**Theme:** Vivid Soul (dark base + soft neon accents).  
**Design language:** glassy panels, soft shadow, 12–18px radius, 8px grid.

## Motion
- UI controls: ≤ 250ms, easeOutCubic / easeInOutQuad
- Scene transitions: ≤ 600ms
- Reduced motion toggle disables non-essential animations

## Layout Regions
1. **Aurora Bar** — ambient HUD + search (Ctrl+K)
2. **Center Stage** — Focus Canvas (Aurora Ring + 2–3 cards)
3. **Right Dock** — command palette, quick actions, intent results
4. **Left Presence** — avatar face, dialogue, controls
5. **Status Ribbon** — timer + quick toggles

## Button System
Juicy tactile buttons with hover lift, press squish, spring release, and optional microburst on success.

## Accessibility
- Reduced motion
- High contrast
- Quiet mode (no sounds)
- Dyslexia-friendly spacing
- Minimal mode (hide non-essential panels)

## Demo Mode
Demo scripts live in `assets/demo/demo_script_01.json` and are viewable/editable from the Demo panel.

## Placeholder Assets
See `assets/avatar` and `assets/audio` for non-binary placeholder files.

## Screenshot Instructions
1. Run: `python main.py`
2. Open Demo Mode (`Ctrl+Shift+D`) and focus canvas (`Ctrl+1`)
3. Capture the window (desktop screenshot tool) or use the browser tool if available.

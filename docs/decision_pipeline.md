# Etherea Decision Pipeline

## Purpose
Describe the core decision flow from input to action. This is documentation only.

## Pipeline
1. **Input**
   - Sources: UI command palette, CLI, sensors, mock server.
   - Inputs are normalized into a shared event shape (see `docs/event_model.md`).

2. **Interpret**
   - Workspace controller parses commands.
   - EI engine interprets signal updates from sensors.
   - Optional voice input is treated as command text.

3. **Decide**
   - Workspace manager applies mode/session changes.
   - Behavior planner selects gestures/voice/motion responses.
   - Overrides/kill-switch policy is checked before acting.

4. **Act**
   - UI updates (console + avatar visuals).
   - Optional audio/voice playback.
   - Motion/gesture playback when available.

5. **Log**
   - UI console messages and optional logs.
   - Errors are handled as non-fatal where possible.

## Notes
- This pipeline reflects current boundaries and optional dependencies.
- No new behavior is implied beyond existing modules.

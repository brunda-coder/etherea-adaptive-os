# Etherea High-Company Validation

## Part 0 — Repo Truth Scan

### Key module map
- **Desktop entrypoint + primary window**: `main.py` bootstraps `AppController`, which creates `EthereaMainWindowV3` as the primary desktop window.
- **Avatar renderer + expression pipeline**: `corund/ui/avatar/avatar_world_widget.py` drives the scene/entity tick loop; `corund/ui/avatar/avatar_entity.py` applies blink/pulse/mouth + mood; `corund/ui/avatar_panel.py` maps emotion vectors into avatar mood states.
- **Offline brain + brain.json loader**: `corund/avatar_engine.py` loads `corund/assets/brain.json` with in-code fallback and emits `{response, command, save_memory, emotion_update}`.
- **Workspace agent/router/controller + boundaries**: `corund/workspace_ai/router.py` parses local commands; `corund/workspace_ai/workspace_controller.py` dispatches actions; `corund/workspace_ai/safe_file_agent.py` enforces allowed-root and extension allowlist restrictions.
- **WebOS build/deploy roots**: `etherea-webos/` is the web root; hosting config is `etherea-webos/firebase.json`; deploy workflow is `.github/workflows/firebase-hosting.yml`.

### Feature Compliance Report
- ✅ **Alive avatar** — Scene bounds are initialized defensively and idle animation loop is active.
- ✅ **Offline brain** — Local `brain.json` + fallback loader is default; command flow now updates emotions and dialogue from offline payload.
- ⚠️ **Theme system (candy polish)** — Existing tokens and persistence are present, but deeper per-surface token controls are still incremental.
- ✅ **Workspace agent safety** — Default-deny roots, persisted approved root command, extension allowlist, and file commands including list/summarize/create/edit.
- ✅ **Web deploy** — Deploy workflow now builds core/ui/web explicitly from `etherea-webos` and prints deployed URL.
- ✅ **CI builds (Android/Windows/Web)** — Android + Tauri ensure scripts and runtime assertions are already wired in release workflows.

## Part 7 — How to test checklist

1. **Desktop startup**
   - Launch desktop app.
   - Confirm Boot Health HUD shows Avatar/Assets/Audio/Brain/Workspace Agent/Sensors/Kill state.
   - Confirm avatar is visible immediately and continues subtle movement/blink.

2. **Offline brain**
   - Enter normal and teach-style prompts.
   - Verify responses are local and characterful.
   - Verify response never includes AI self-identification phrases.

3. **Workspace agent safety**
   - Run `allow workspace root <path>`.
   - Run `create file`, `edit file`, `summarize file`, `list workspace files depth 2`.
   - Verify out-of-root and disallowed extension operations are denied.

4. **Web build**
   - Run `npm run build -w @etherea/web` from `etherea-webos`.

5. **Firebase deploy**
   - Run GitHub Action `Firebase Hosting Deploy` on `main`.
   - Confirm logs show deployed hosting URL and the live site serves index + assets.

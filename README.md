# Etherea — Your Living Adaptive OS 🌌✨ (v3.0.999)
---

> **A desktop-first operating environment that adapts to you, not the other way around.**  
> Built for **interactive professor demos**: you (the presenter) + Etherea (the heroine avatar) co-present like real collaborators.

✅ **Canonical current build doc**: See `ETHEREA_CORE.md` (this is what Etherea should explain as).

---

## ✨ What’s New (v3.0.999)

This release is the **report-aligned demo build** focused on:
- **Presenter Mode** + gentle “alive” ambient motion
- **Co-present script** (Etherea speaks short, demo-safe lines alongside the human presenter)
- **Demo-friendly expressives**: `dance`, `hum`, `surprise`
- **FocusGuardian supervisor** (nudges during strict focus sessions, safe + non-invasive)
- **Release-only CI** (build/tests run only when a GitHub Release is published — no spammy Actions)

---

## Status (Reality Check)

**Working**
- Desktop PySide6 UI (`core/ui/main_window_v2.py`) with **Heroine avatar + console + command palette**.
- Presenter demo commands: `present on/off`, `co-present`, `next`, `skip`, `dance`, `hum`, `surprise`.
- Workspace command routing + session memory logic (CLI + UI-safe).
- Background audio engine + voice output adapters (optional dependencies).

**Partially working / optional**
- HID sensors and EI signal updates (OS-dependent; requires `pynput`).
- Voice input (SpeechRecognition + microphone; may require system audio deps).
- Flask mock web server (`server.py`) with simulated EI/status data.

**Planned / conceptual (docs only)**
- Some docs/specs describe a broader roadmap and UI spec ideas. These are clearly marked as conceptual/spec and are not guaranteed to be fully implemented.

---
=======

## ✨ What’s New (v3.0.999)

This release is the **report-aligned demo build** focused on:
- **Presenter Mode** + gentle “alive” ambient motion
- **Co-present script** (Etherea speaks short, demo-safe lines alongside the human presenter)
- **Demo-friendly expressives**: `dance`, `hum`, `surprise`
- **FocusGuardian supervisor** (nudges during strict focus sessions, safe + non-invasive)
- **Release-only CI** (build/tests run only when a GitHub Release is published — no spammy Actions)

---

## Status (Reality Check)

**Working**
- Desktop PySide6 UI (`core/ui/main_window_v2.py`) with **Heroine avatar + console + command palette**.
- Presenter demo commands: `present on/off`, `co-present`, `next`, `skip`, `dance`, `hum`, `surprise`.
- Workspace command routing + session memory logic (CLI + UI-safe).
- Background audio engine + voice output adapters (optional dependencies).

**Partially working / optional**
- HID sensors and EI signal updates (OS-dependent; requires `pynput`).
- Voice input (SpeechRecognition + microphone; may require system audio deps).
- Flask mock web server (`server.py`) with simulated EI/status data.

**Planned / conceptual (docs only)**
- Some docs/specs describe a broader roadmap and UI spec ideas. These are clearly marked as conceptual/spec and are not guaranteed to be fully implemented.

---

>>>>>>> 0386245 (ADDED NEW README, PYTEST, AND CONFTEST)
## Install & Run

### Windows (Release ZIP)
1. Click **Windows Download** at the top.
2. Extract the ZIP.
3. Run the EXE inside.
4. If Windows SmartScreen appears (unsigned academic build):  
   **More info → Run anyway**

### Linux (AppImage)
1. Click **Linux Download** at the top.
2. Make it executable:
    chmod +x EthereaOS_Linux.AppImage
3. Run:
    ./EthereaOS_Linux.AppImage

### Local Python (Dev)
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python main.py

Optional entrypoints:
    python core/ui/main_window_v2.py   # main UI (hero demo)
    python etherea_launcher.py         # HiDPI-safe desktop launcher
    python etherea_workspace_cli.py    # CLI command routing
    python server.py                   # Flask mock web UI

---

## Quick Demo Commands (Professor-Friendly)

Command palette / input supports:

**Presenter layer**
- present on
- present off
- co-present
- next
- skip

**Cinematic demo spice**
- dance
- hum
- surprise

**Workspace routing**
- study mode
- coding mode
- exam mode
- calm mode
- save session
- continue last session
- focus 25 minutes

---
## Documentation Map (Source of Truth)

- **ETHEREA_CORE.md**: Canonical current demo behavior + commands (the “truth doc”).
- **README.md**: Current release overview + run steps + demo commands.
- **docs/**: Concept/design docs (bannered so old/planned text doesn’t confuse the current demo).
- **specs/**: UI/roadmap specs (bannered; not all implemented).

---

## Architecture (Mermaid)

### System Overview
~~~mermaid
flowchart TD
  U[User] --> UI[Desktop UI Layer]
  UI --> WC[WorkspaceController]
  WC --> WM[WorkspaceManager]
  WC --> Router[WorkspaceAIRouter]

  UI --> BP[Behavior Planner]
  BP --> GE[Gesture Engine]
  GE --> AR[Aurora Ring FX]

  WM --> SM[Session Memory]
  WM --> Modes[Workspace Modes]

  UI --> Audio[Background Audio Engine]
  UI --> Voice[Avatar Voice Output]
~~~


### Workspace Command Flow
~~~mermaid
sequenceDiagram
  participant U as User
  participant CP as Command Palette / Command Input
  participant WC as WorkspaceController
  participant WM as WorkspaceManager

  U->>CP: "coding mode"
  CP->>WC: handle_command()
  WC->>WM: apply_mode("coding")
  WM-->>WC: ok + state
  WC-->>CP: output/log
~~~
<<<<<<< HEAD
## Release & CI (No Spam Actions)

Workflows run **only** when a GitHub Release is **published**:
- `.github/workflows/release-tests.yml` (pytest on release)
- `.github/workflows/release-build.yml` (Windows build on release)

Important: The download buttons above expect these exact asset names:
- `EthereaOS_Windows.zip`
- `EthereaOS_Linux.AppImage`

---
=======

---

## Release & CI (No Spam Actions)

Workflows run **only** when a GitHub Release is **published**:
- `.github/workflows/release-tests.yml` (pytest on release)
- `.github/workflows/release-build.yml` (Windows build on release)

Important: The download buttons above expect these exact asset names:
- `EthereaOS_Windows.zip`
- `EthereaOS_Linux.AppImage`

---

>>>>>>> 0386245 (ADDED NEW README, PYTEST, AND CONFTEST)
## Full Repository Tree (Big + Exact)

~~~text
etherea-tutorial/
├── .github/
│   └── workflows/
│       ├── release-build.yml
│       └── release-tests.yml
├── .gitignore
├── ETHEREA_CORE.md
├── Makefile
├── README.md
├── apply_etherea_upgrade.sh
├── core/
│   ├── __init__.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base_adapter.py
│   │   ├── code_adapter.py
│   │   ├── document_adapter.py
│   │   ├── media_adapter.py
│   │   ├── pdf_adapter.py
│   │   └── spreadsheet_adapter.py
│   ├── agent.py
│   ├── app_controller.py
│   ├── app_registry.py
│   ├── app_runtime.py
│   ├── assets/
│   │   ├── animations/
│   │   │   └── splash_pulse.json
│   │   ├── audio/
│   │   │   ├── etherea_theme_a.wav
│   │   │   ├── etherea_theme_b.wav
│   │   │   └── etherea_theme_c.wav
│   │   ├── avatar.png
│   │   ├── avatar_manifest.json
│   │   ├── etherea_assets_manifest.json
│   │   └── models/
│   │       ├── aurora_placeholder.bin
│   │       └── aurora_placeholder.gltf
│   ├── audio_analysis/
│   │   ├── beat_detector.py
│   │   ├── beat_to_ui.py
│   │   ├── song_cache.py
│   │   ├── song_resolver.py
│   │   └── songdance.txt
│   ├── audio_engine.py
│   ├── aurora_pipeline.py
│   ├── aurora_state.py
│   ├── avatar_behavior.py
│   ├── avatar_engine.py
│   ├── avatar_motion/
│   │   ├── dance_planner.py
│   │   ├── motion_catalog.json
│   │   └── motion_controller.py
│   ├── avatar_scripts.py
│   ├── avatar_system.py
│   ├── avatar_visuals.py
│   ├── behavior/
│   │   └── behavior_planner.py
│   ├── database.py
│   ├── ei_engine.py
│   ├── emotion_mapper.py
│   ├── event_bus.py
│   ├── event_model.py
│   ├── gestures/
│   │   ├── gesture_engine.py
│   │   └── presets.py
│   ├── md_loader.py
│   ├── memory_store.py
│   ├── os_adapter.py
│   ├── os_pipeline.py
│   ├── resource_handler.py
│   ├── runtime_state.py
│   ├── self_awareness/
│   │   └── introspector.py
│   ├── signals.py
│   ├── system_tools.py
│   ├── tutorial_flow.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── aurora_canvas_widget.py
│   │   ├── aurora_ui.py
│   │   ├── avatar_engine/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py
│   │   │   └── registry.py
│   │   ├── avatar_engine_widget.py
│   │   ├── avatar_heroine_widget.py
│   │   ├── avatar_widget.py
│   │   ├── beat_sync.py
│   │   ├── bubbles.py
│   │   ├── command_palette.py
│   │   ├── explorer.py
│   │   ├── gui.py
│   │   ├── holograms.py
│   │   ├── icon_provider.py
│   │   └── main_window_v2.py
│   ├── utils/
│   │   └── asset_path.py
│   ├── utils.py
│   ├── voice_adapters.py
│   ├── voice_engine.py
│   ├── workspace_ai/
│   │   ├── __init__.py
│   │   ├── focus_mode.py
│   │   ├── router.py
│   │   ├── session_memory.py
│   │   ├── task_extractor.py
│   │   ├── workspace_ai_hub.py
│   │   ├── workspace_controller.py
│   │   └── workspace_profiles.json
│   ├── workspace_manager.py
│   └── workspace_registry.py
├── data/
│   └── apps.json
├── deployment_guide.md
├── docs/
│   ├── 07_privacy_permissions_and_user_control.md
│   ├── RELEASE.md
│   ├── architecture_map.md
│   ├── aurora_canvas.md
│   ├── avatar_visuals.md
│   ├── decision_pipeline.md
│   ├── eisignal_awareness.md
│   ├── etherea_overview.md
│   ├── etherea_v2_docs.md
│   ├── event_model.md
│   ├── experience.md
│   ├── notes.md
│   ├── os_integration.md
│   ├── overrides_policy.md
│   ├── permissions.md
│   ├── preferences.md
│   ├── rules.md
│   ├── state_model.md
│   ├── user_profile_and_identity.md
│   └── workspace_and_focus.md
├── eav.sh
├── etherea_dance_timeline.json
├── etherea_launcher.py
├── etherea_safe_check.py
├── etherea_workspace_cli.py
├── exports/
│   └── export_20260114_1424.zip
├── index.html
├── main.py
├── pytest.ini
├── requirements-core.txt
├── requirements-desktop.txt
├── requirements-ui.txt
├── requirements.txt
├── safe_check_report.txt
├── safe_check_report_after_gestures.txt
├── safe_check_report_after_planner.txt
├── safe_check_report_dance.txt
├── safe_check_report_dance_auto.txt
├── safe_check_report_motion.txt
├── safe_check_report_songdance.txt
├── safe_check_report_v3_0_29.txt
├── script.js
├── scripts/
│   └── etherea-doctor
├── sensors/
│   ├── __init__.py
│   ├── hid_sensor.py
│   ├── keyboard_sensor.py
│   └── mouse_sensor.py
├── server.py
├── setup_data.py
├── setup_key.py
├── specs/
│   ├── etherea_roadmap.md
│   └── etherea_ui.md
├── src/
│   └── m_top_k_frequent_words_from_text.py
├── style.css
├── test_translucency.py
├── test_voice_isolated.py
├── tests/
│   ├── conftest.py
│   ├── test_ei_hierarchy.py
│   ├── test_ei_logic.py
│   ├── test_m_top_k_frequent_words_from_text.py
│   ├── test_mapping_constraints.py
│   ├── test_memory.py
│   ├── test_sensors.py
│   └── test_translucency.py
└── workspace/
    ├── .etherea_last_session.json
    ├── doc_142113.txt
    └── doc_142114.txt
~~~
---

## Diagnostics (Termux / CLI Safe Mode)

Safe health report:
<<<<<<< HEAD
  ```
    python etherea_safe_check.py | tee safe_check_report.txt
  ```
Compile check:
   ```
    python -m compileall core | tee compile_report.txt
  ```
Minimal smoke harness (CLI-safe):
   ```
    python -m compileall core
    python etherea_safe_check.py
    python etherea_workspace_cli.py
  ```
=======
    python etherea_safe_check.py | tee safe_check_report.txt

Compile check:
    python -m compileall core | tee compile_report.txt

Minimal smoke harness (CLI-safe):
    python -m compileall core
    python etherea_safe_check.py
    python etherea_workspace_cli.py

>>>>>>> 0386245 (ADDED NEW README, PYTEST, AND CONFTEST)
---

## Contributing (From Repository Root)

1. Fork the repo and clone:
<<<<<<< HEAD
```
   git clone https://github.com/<your-username>/etherea-tutorial.git
    cd etherea-tutorial
```
3. Create a branch:
```
   git checkout -b feature/your-feature-name
```
4. Run checks:
```
   python -m compileall core
    python etherea_safe_check.py
```
5. Commit:
   ```
   git add .
    git commit -m "Add: <short description>"
   ```
6. Push + PR:
   ```
    git push origin feature/your-feature-name
   ```
=======
    git clone https://github.com/<your-username>/etherea-tutorial.git
    cd etherea-tutorial

2. Create a branch:
    git checkout -b feature/your-feature-name

3. Run checks:
    python -m compileall core
    python etherea_safe_check.py

4. Commit:
    git add .
    git commit -m "Add: <short description>"

5. Push + PR:
    git push origin feature/your-feature-name

>>>>>>> 0386245 (ADDED NEW README, PYTEST, AND CONFTEST)
---

## Contributors

**Brunda G**: Core coordinator, logic flow, real frontend and backend logic creator, Planner  
**Chandramma**: Database management exclusively on Etherea and data/.md creator  
**Chinmai HA**: Database management assistance, API key integration  
**Ayatunnisa**: Creative head and design logic  
**Arshiya Khanum**: Debugger and tester  
**Azra Rahman**: Hardware and software analyser  
**ChatGPT**: Documentation and planning  
**Google Antigravity**: Agentic assistance  

<p align="center">
  <b>Powered by the Aureth Team</b><br>
  Rooted in <b>JNNCE, Shimoga, Karnataka, India</b>
</p>

---

## Authors (Team Details)

| Name | USN |
|------|-----|
| Brunda G | 4JN25CS039 |
| CHANDRAMMA | 4JN25CSO47 |
| AYATHUNNISA | 4JN25CS025 |
| Chinmai HA | 4JN25CS051 |
| Arshiya Khanum | 4JN25CS022 |
<<<<<<< HEAD
| Azra Rahman | 4JN25CS026
=======
| Azra Rahman | 4JN25CS026 |

>>>>>>> 0386245 (ADDED NEW README, PYTEST, AND CONFTEST)

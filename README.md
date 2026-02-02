# Etherea — Your Living Adaptive OS 🌌✨ (v3.1.0)
---

> **A desktop-first operating environment that adapts to you, not the other way around.**  
> Built for **interactive professor demos**: you (the presenter) + Etherea (the heroine avatar) co-present like real collaborators.

✅ **Canonical current build doc**: See `ETHEREA_CORE.md` (this is what Etherea should explain as).

---

## ✨ What’s New (v3.1.0)

This release focuses on stability, developer experience, and refining the core demo features:
- **Git Repository Fix**: Resolved critical push errors by properly ignoring `node_modules` and removing large files from history. Your repository is now clean and stable.
- **Presenter & Demo Commands**: Enhanced and clarified the presenter-focused commands. Etherea is now better equipped for co-presentations.
- **Updated Feature List**: The README now reflects the current, working features of the application, removing outdated information.
- **Focus on Core Python App**: Instructions are clarified to emphasize the main Python-based desktop application.
- **Dependency Management**: Standardized dependency handling by ensuring `node_modules` and other large build artifacts are ignored.

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
## Install & Run

### Local Python (Dev)
This is the recommended way to run the application for development.

```
# Set up a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the main application
python main.py
```

Optional entrypoints:
```
python core/ui/main_window_v2.py   # main UI (hero demo)
python etherea_workspace_cli.py    # CLI command routing
python server.py                   # Flask mock web UI
```

---

## Quick Demo Commands (Professor-Friendly)

Command palette / input supports:

**Presenter layer**
- `present on`: Activates presenter mode.
- `present off`: Deactivates presenter mode.
- `co-present`: Etherea will deliver lines from a script.
- `next`: Move to the next line in the script.
- `skip`: Skip a line in the script.

**Cinematic demo spice**
- `dance`: Etherea performs a dance animation.
- `hum`: Etherea hums a tune.
- `surprise`: Etherea shows a surprised expression.

**Workspace routing**
- `study mode`
- `coding mode`
- `exam mode`
- `calm mode`
- `save session`
- `continue last session`
- `focus 25 minutes`

---
## Documentation Map (Source of Truth)

- **ETHEREA_CORE.md**: Canonical current demo behavior + commands (the “truth doc”).
- **README.md**: Current release overview + run steps + demo commands.
- **docs/**: Concept/design docs (bannered so old/planned text doesn’t confuse the current demo).
- **specs/**: UI/roadmap specs (bannered; not all implemented).

---

## Contributing (From Repository Root)

1. Fork the repo and clone:
```
git clone https://github.com/<your-username>/etherea-tutorial.git
cd etherea-tutorial
```
2. Create a branch:
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
| Azra Rahman | 4JN25CS026 |

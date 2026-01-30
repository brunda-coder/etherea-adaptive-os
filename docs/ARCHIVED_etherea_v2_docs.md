> ⚠️ **ARCHIVED DOC (OLD VERSION)**
> This file describes Etherea v2-era structure. Current behavior and demo commands are documented in **ETHEREA_CORE.md**.

# Etherea v2 Project Documentation

## Architecture Overview
Etherea v2 is a desktop-first prototype designed to explore emotional intelligence, adaptive UI, and command routing.

## Core Concepts (Terminology)
- **Etherea**: desktop-first adaptive workspace system.  
- **Avatar**: EI talking UI.  
- **Aurora**: mood/time-based GUI canvas concept with aura ring + search foundation.  
- **Ethera**: natural-language command interpreter (routing layer).  

### Components
1. **Core / UI**: PySide6 widgets (`core/ui/main_window_v2.py`, `avatar_widget.py`, `aurora_ui.py`).
2. **EI Engine**: Emotion state updates wired through `core/ei_engine.py` and `core/signals.py`.
3. **Sensors**: Optional HID sampling via `sensors/hid_sensor.py` (requires `pynput`).
4. **Memory**: Session + workspace memory (`core/memory_store.py`, `core/workspace_ai/session_memory.py`).

## Getting Started
### Prerequisites
- Python 3.10+
- PySide6, numpy
- Optional: pynput (HID sensors), SpeechRecognition + audio backend (voice input), pyttsx3/edge-tts (voice output), Flask (mock web UI)

### Setup
1. Clone the repository.
2. Run `python setup_data.py` to initialize the database (optional).
3. Start the application with `python main.py`.
4. Optional entrypoints: `python etherea_launcher.py` (HiDPI launcher), `python etherea_workspace_cli.py` (CLI router), `python server.py` (Flask mock).

## Developer Guide
- **Adding Sensors**: Implement a class in `sensors/` and connect to `signals.input_activity`.
- **UI Customization**: Modify `core/ui/avatar_widget.py` (aurora ring drawing) or `core/ui/main_window_v2.py` (layout/controls).
- **Memory API**: Use `MemoryStore.add_to_ltm` and `MemoryStore.search_ltm`.

## Testing
Run `pytest tests/` to validate core logic.

## Current Status
**Working**
- Desktop UI with heroine avatar + aurora ring drawing.
- Workspace command routing + session memory.
- Background audio + voice output adapters (optional dependencies).

**Partially working / optional**
- HID sensors + EI updates (OS-dependent).
- Voice input (requires microphone + SpeechRecognition backend).
- Flask mock server for web demo.

**Planned (existing docs only)**
- Additional UI polish + behavior hooks listed in `specs/etherea_roadmap.md`.
- Lip-sync and advanced motion remain deferred.

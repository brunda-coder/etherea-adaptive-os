> 🟡 **CONCEPT / DESIGN DOC**
> This file may describe a broader or planned model. For the **current working demo behavior and commands**, see **ETHEREA_CORE.md**.

# Etherea Architecture Map (One Page)

## Core components
- **UI Shell (desktop-first)**: `core/ui/main_window_v2.py` hosts the EI avatar panel and the Aurora canvas surface.
- **Avatar System (EI heroine)**: `core/ui/avatar_heroine_widget.py`, `core/avatar_behavior.py`, `core/avatar_visuals.py`, `core/voice_engine.py`.
- **Aurora Canvas (OS surface)**: `core/ui/aurora_canvas_widget.py`, `core/aurora_state.py`, `core/aurora_pipeline.py`.
- **Ethera Command & Policy**: `core/workspace_ai/*` (command interpretation), `core/behavior/*`.
- **Workspace System**: `core/workspace_manager.py`, `core/workspace_registry.py`.
- **OS Integration**: `core/os_adapter.py`, `core/os_pipeline.py`, `core/app_registry.py`.
- **Event Spine**: `core/event_model.py`, `core/event_bus.py`.

## Boundaries (who owns what)
- **UI**: renders state only; it emits intents but does not execute actions.
- **Pipelines**: resolve intents, enforce overrides, emit events, and update state.
- **State stores**: single runtime state model + Aurora state store as derived view.
- **OS adapter**: isolated execution layer with DRY_RUN support.

## State ownership
- **Runtime state**: `core/runtime_state.py` (single source of truth).
- **AuroraCanvasState**: computed from runtime state + action registry (`core/aurora_state.py`).
- **Workspace registry**: persistent snapshot of workspaces + session data (`core/workspace_registry.py`).

## Event flow (simplified)
Input → Interpret → Policy → Decide → Act → Log  
- UI emits intent → Aurora/Ethera pipeline decides → OS adapter (if needed) → events emitted → UI updates.

## Conceptual vs implemented
- **Implemented**: Aurora canvas, workspace registry, OS adapter pipeline, event spine, avatar visuals.
- **Conceptual**: advanced avatar animation (lip-sync/full-body) remains deferred.
# Etherea Architecture Map (1-page)

## Scope
Desktop-first prototype with a PySide6 UI, EI signal routing, optional sensors/voice, and workspace command routing. Voice/audio support remains enabled; advanced avatar animation remains deferred.

## Components & Boundaries

### UI Layer (Desktop)
- **Entry points**: `main.py`, `etherea_launcher.py`.
- **Primary window**: `core/ui/main_window_v2.py` (heroine avatar + console + command palette).
- **Avatar visuals**: `core/ui/avatar_widget.py`, `core/ui/avatar_heroine_widget.py`.
- **Aurora ring drawing**: `core/ui/avatar_widget.py`.

**Boundary**: UI consumes state and emits user intents/commands; it does not own core state or storage.

### Engine & Behavior
- **EI engine**: `core/ei_engine.py` updates emotional signals.
- **Behavior planning**: `core/behavior/behavior_planner.py` generates gesture/voice/motion plans.
- **Gesture system**: `core/gestures/gesture_engine.py` and `core/gestures/presets.py`.
- **Avatar motion**: `core/avatar_motion/*` (basic motion + dance planning; advanced animation deferred).

**Boundary**: Engine computes signals and plans; UI renders results and triggers playback.

### Workspace Logic
- **Workspace manager**: `core/workspace_manager.py`.
- **Command routing**: `core/workspace_ai/router.py`, `core/workspace_ai/workspace_controller.py`.
- **Session memory**: `core/workspace_ai/session_memory.py`.

**Boundary**: Workspace logic owns session state and command interpretation; UI/CLI call into it.

### Audio & Voice (Optional)
- **Background audio**: `core/audio_engine.py`.
- **Voice**: `core/voice_engine.py`, `core/voice_adapters.py`.

**Boundary**: Voice/audio are optional services; callers should tolerate missing deps.

### Sensors (Optional)
- **HID sensors**: `sensors/hid_sensor.py`, `sensors/keyboard_sensor.py`, `sensors/mouse_sensor.py`.

**Boundary**: Sensors emit input-activity signals; core consumes them to update EI state.

### CLI + Mock Server
- **CLI**: `etherea_workspace_cli.py` (workspace command routing).
- **Mock server**: `server.py` (Flask demo endpoints, simulated EI status).

**Boundary**: Non-desktop entrypoints route through the same workspace or mock data paths.

## State Ownership
- **UI state** (window layout, visuals): owned by UI widgets.
- **Runtime state** (EI vector, workspace mode, session memory): owned by core engine/workspace modules.
- **Audio/voice state**: owned by audio/voice services.
- **Sensor state**: owned by sensor modules.

## Data/Signal Flow (High-level)
1. **User intent** → UI/CLI → Workspace controller → Workspace manager/session memory.
2. **Sensors** → signals → EI engine → UI updates (avatar + console).
3. **Behavior planner** → gesture/motion/voice plans → UI playback.
4. **Audio/voice** services run optionally; failures are non-fatal.

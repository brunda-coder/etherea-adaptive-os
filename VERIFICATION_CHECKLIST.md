# ETHEREA Build Verification Checklist

This document tracks the project's alignment with the "ETHEREA – THE LIVING ADAPTIVE OPERATING SYSTEM" blueprint.

## Core Identity & Tech Stack

- [ ] **Desktop-First:** Core application is a Python desktop app, not web-based.
- [ ] **UI:** PySide6 is the designated UI framework.
- [ ] **Database:** SQLite is used for local-first storage.
- [x] **AI Layer:** System is built on an agent-based architecture.
- [ ] **Internet:** Core functionality is offline-capable.

## System Architecture

- [x] **Event Bus:** A central `event_bus` is implemented and used for system-wide communication.
- [x] **Global State Model:** A global `EthereaState` object is implemented and tracks key metrics (focus, load, etc.).
- [x] **Policy/Decision Engine:** An autonomous engine evaluates state and makes decisions.
- [x_] **Decision Logging:** All agent decisions are logged.
- [x] **Tool Router:** A tool router executes agent-chosen actions.

## Workspace System

- [x] **Multiple Workspaces:** System supports multiple, functionally distinct workspaces.
- [x] **Required Workspaces:** `Study`, `Build`, `Research`, `Calm`, `Deep Work` are implemented.
- [x] **Workspace-Specific Behavior:** Each workspace correctly modifies agent autonomy, UI, aura, and other system parameters.

## Autonomous Agent Assistance

- [ ] **Proactive Assistance:** Agents can act without direct commands based on context.
- [ ] **Context-Aware Actions:** Assistance is relevant to the user's activity (e.g., summarizing a PDF during idle scroll).
- [ ] **Selective Inaction:** Agents correctly identify moments to stay silent (e.g., Deep Work mode).

## Document & PDF Intelligence

- [ ] **PDF Talk:** PDFs can be opened and interacted with through an agent.
- [ ] **Local-First PDF Analysis:** PDF features work locally where possible.
- [ ] **Document Assist:** Agent assistance is available within document editors.

## Code Editor Assistance

- [ ] **Integrated Code View:** A code editor is part of the Etherea UI.
- [ ] **Code-Aware Agent:** The agent can read, explain, and suggest fixes for code.

## Avatar & Aurora

- [ ] **Avatar Expression State Machine:** Avatar has and uses the required expression states.
- [ ] **State-Driven Expressions:** Avatar expressions are driven by the global `EthereaState`.
- [ ] **Dynamic Aurora UI:** The Aurora is a live-rendered UI element.
- [ ] **State-Driven Aurora:** Aurora's appearance (intensity, color, speed) is driven by the global `EthereaState`.

## Privacy & Memory

- [ ] **Local-First Storage:** All core data is stored in a local SQLite database.
- [ ] **No Silent Transmission:** No data is transmitted without explicit consent.
- [ ] **Enforced Privacy Layer:** Privacy rules are a non-negotiable system layer, respected by all agents.
- [ ] **Memory System:** SQLite database contains the required tables (`sessions`, `events`, etc.).
- [ ] **User Memory Controls:** User has full control over their data (delete, disable learning).

## Forbidden Elements Check

- [ ] **No Generic Dashboards:** UI is purposeful and adaptive.
- [ ] **No Fake Widgets:** All UI elements are functional.
- [ ] **No Placeholders:** All text and content are real or dynamically generated.
- [ ] **Not Web-Only:** The primary product is a desktop application.
- [ ] **No Cloud-Only Logic:** Core logic runs locally.

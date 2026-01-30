> ⚠️ **ARCHIVED DOC (OLD VERSION)**
> This roadmap reflects earlier planning. Current demo behavior & commands: **ETHEREA_CORE.md**.

# Etherea v2 Roadmap: Core System

## Goal
Build core modules for Etherea’s adaptive desktop OS with Emotional Intelligence (EI), multi-modal sensors, and advanced UI/UX.

## System Architecture Outline
- **Sensor Layer**: High-frequency sampling (120Hz) of user inputs (HID).
- **EI Processor**: State machine for emotion/focus/stress transitions.
- **Memory Layer**: Persistent Long-Term Memory (LTM) with semantic embedding cache.
- **Action Buffer**: Queue for proactive assistant responses and UI feedback.
- **UI UX Layer**: Aurora Ring procedural animations and translucent holographic overlays.

## Data Flow
`sensors` → `EI Processor` → `Memory Management` → `Action Loop` → `UI Renderer`

## EI State Machine Transitions
- **IDLE**: Low focus, low stress.
- **FLOW**: High focus, stable pulse/input velocity.
- **STRESS**: High input erraticism, high frequency keyboard bursts.
- **FATIGUE**: Low input velocity over time, high error rate.

## Aurora Ring Spec
- **Procedural Animation**: Dynamic particle orbits changing color and speed based on EI state.
- **Reactive**: Pulse on voice activity, glow intensity tied to focus.

## Voice Pipeline
- **Command Parsing**: "Ethera" wake word.
- **Pipeline**: Audio Stream → STT → NLU Intent → Intent Execution → TTS Feedback.

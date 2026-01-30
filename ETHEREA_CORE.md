# ETHEREA — The Living Desktop OS (Current Build)

Etherea is a **desktop-first** “Living OS” prototype: a focused workspace environment guided by an emotionally aware heroine avatar.  
This build is designed for **interactive professor demos**: you (the presenter) and Etherea (the system) collaborate like co-speakers.

---

## What Etherea is (in one line)
A productivity-first desktop companion that adapts presentation + focus modes and communicates intent visibly through an avatar + aurora UI.

---

## Core Modules (Current)

### 1) Heroine Avatar (Emotional UI)
- The avatar is the “front face” of the system: expressive and responsive.
- Visible expressive actions (demo-safe):
  - `dance` → toggles expressive “dance” behavior (presenter-friendly animation mode)
  - `hum` → toggles expressive humming mode
  - `surprise` → triggers cinematic UI pulse + gesture (if supported)

### 2) Aurora Canvas (Intent UI)
- Aurora acts as a **visual intent surface** that reflects current mode/state and can route simple actions through the pipeline.

### 3) Workspace Controller (Focus Modes)
- Modes are designed to keep the agent focused and the UI predictable:
  - study / coding / exam / calm / deep_work
- Focus sessions support a timer-style workflow (example: 25-minute focus).

### 4) Voice (Optional)
- Voice can be enabled if dependencies are available.
- Supports short commands + optional wake loop (environment dependent).

---

## Presenter Layer (Professor Demo)

### Presenter Mode
- `present on` / `present off` enables gentle ambient “breathing” effects so the UI feels alive.

### Co-present Script
- `co-present` starts a short script where Etherea speaks brief lines that complement the human presenter.
- `next` moves to the next talking point; `skip` fast-forwards.

---

## Demo Commands (Quick)
- `present on` / `present off`
- `co-present` / `next` / `skip`
- `dance` / `hum` / `surprise`

---

## Notes / Scope Boundaries (Report-safe)
This prototype emphasizes **interaction + adaptive UX**. Full “premium editor replacement” capabilities (PDF/video/photo) are out of scope for this demo build unless explicitly implemented as separate modules.

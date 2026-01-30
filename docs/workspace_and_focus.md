> 🟡 **CONCEPT / DESIGN DOC**
> This file may describe a broader or planned model. For the **current working demo behavior and commands**, see **ETHEREA_CORE.md**.

# Workspace States & Focus Modes

This document explains how Etherea understands **workspace state**
and how it switches between different **focus modes**.

> **Note:** The current implementation exposes a smaller set of command-driven modes
(`study`, `coding`, `exam`, `calm`) via `core/workspace_ai/workspace_controller.py`.
The broader state taxonomy below is conceptual and not fully wired yet.

Written for beginners.
No coding knowledge is required.

---

## 1. What is a Workspace State?

A **workspace state** describes:
- How focused the user currently is
- What kind of activity is happening
- How intense or relaxed the environment should be

Think of it like a **mood + task snapshot** of the workspace.

Example:
- Studying calmly
- Working deeply
- Feeling distracted
- Feeling stressed
- Taking a break

The system does NOT guess randomly.
It **observes signals** and adjusts carefully.

---

## 2. Why Workspace States Matter

Without workspace states:
- The system behaves the same all the time
- No adaptation feels meaningful
- Avatar responses feel robotic

With workspace states:
- UI changes make sense
- Notifications are controlled
- Avatar tone feels natural
- Environment feels supportive

Workspace states are the **bridge** between signals and actions.

---

## 3. What is a Focus Mode?

A **focus mode** is a named configuration that tells the system:
- What to allow
- What to reduce
- What to emphasize

Focus modes are **user-friendly labels**
for deeper internal logic.

Examples:
- Deep Focus
- Light Work
- Learning Mode
- Creative Mode
- Rest Mode

Users understand modes.
The system handles complexity underneath.

---

## 4. Difference Between State and Mode

Important distinction:

- **Workspace State** → What is happening right now
- **Focus Mode** → How the system should respond

Example:
- State: distracted + high app switching
- Mode applied: Focus Recovery Mode

The system may **suggest** a mode,
but the user always has control.

---

## 5. How Workspace State is Detected (Conceptual)

Etherea does NOT read minds.

It uses:
- App usage patterns
- Interaction speed
- Time spent on tasks
- User feedback
- Manual mode selection

No biometric data is required by default.

Everything is:
- Gradual
- Explainable
- Reversible

---

## 6. Core Workspace States (Initial Set)

For the first version of Etherea, we define:

1. Idle  
2. Light Focus  
3. Deep Focus  
4. Distracted  
5. Overloaded  
6. Resting  

These are enough to start.
More can be added later.

---

## 7. Example: Deep Focus Mode

When Deep Focus is active:
- Notifications are reduced
- UI becomes minimal
- Avatar speaks less, but clearly
- Suggestions are postponed

The system helps **without interrupting**.

---

## 8. User Control Rules (Very Important)

Etherea must always:
- Show when a mode changes
- Explain why it changed
- Allow manual override
- Remember user preferences

No forced automation.
No hidden behavior.

---

## 9. Ethical Design Note

Workspace states:
- Are not judgments
- Are not labels on the user
- Are temporary and fluid

They exist to **support**, not control.

---

## 10. Summary

Workspace states describe what is happening.
Focus modes decide how the system behaves.

Together they allow Etherea to feel:
- Calm
- Intelligent
- Respectful
- Human-centered

This logic is foundational for
avatars, UI behavior, and future intelligence.

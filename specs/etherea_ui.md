> 🟠 **SPEC (NOT FULLY IMPLEMENTED)**
> This is a specification document. Implementation may be partial. For the **current working demo behavior and commands**, see **ETHEREA_CORE.md**.

# Etherea UI Specification

## Overview
Next-generation translucent UI using PySide6. Central focus is the **Aurora Ring**.

## Components
### Aurora Ring
- **Type**: QWidget with Custom QPainter logic.
- **Visuals**: Layered gradients, additive blending, procedural particle glow.
- **EI Mapping**:
| State | Color Palette | Animation Speed |
|-------|---------------|-----------------|
| IDLE  | Cyan / Blue   | Slow            |
| FLOW  | Gold / Green  | Steady          |
| STRESS| Red / Magenta | Rapid / Erratic |
| THINK | White / Silver| Pulsing         |

### Layout Architecture
- Root: `EthereaMainWindow`
- Central: `AuroraContainer`
- Overlays: `HolographicPanel`

## Functional Requirements
- High-frequency UI updates (60fps) for fluid animation.
- Translucency support with blurred background (platform dependent/simulated).
- Global shortcuts for quick command entry.

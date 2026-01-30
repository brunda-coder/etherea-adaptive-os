> 🟡 **CONCEPT / DESIGN DOC**
> This file may describe a broader or planned model. For the **current working demo behavior and commands**, see **ETHEREA_CORE.md**.

# Overrides & Kill-Switch Policy

## Purpose
Document the overrides/kill-switch policy for runtime behavior. This is documentation only and does not change existing behavior.

## Policy
- **Kill-switch**: a single boolean override that disables non-critical subsystems when set.
- **Subsystem overrides**: independent toggles for audio, voice, and sensors.
- **Reason field**: optional text to explain why an override is active.

## Intended Usage
- Overrides should be evaluated early in the runtime decision pipeline before acting on commands or signals.
- If the kill-switch is enabled, UI should continue to render while optional subsystems remain disabled.
- Overrides are meant for safety, diagnostics, and compliance scenarios.

## Alignment With Current Constraints
- Desktop-first remains primary.
- Voice/audio support remain supported unless explicitly overridden.
- Advanced avatar animation remains deferred.

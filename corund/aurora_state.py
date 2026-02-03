from dataclasses import dataclass, field

@dataclass
class AuroraState:
    """
    Represents the visual state of the Aurora effect.
    This is the single source of truth for the Aurora's appearance.
    """
    # The overall brightness and activity level of the aurora.
    # Range: 0.0 (calm) to 1.0 (intense).
    intensity: float = 0.5

    # The speed at which the aurora effect pulses and shifts.
    # Range: 0.5 (slow) to 2.0 (fast).
    pulse_speed: float = 1.0

    # The color temperature of the aurora.
    # Range: 0.0 (cool blues) to 1.0 (warm reds).
    temperature: float = 0.2

    # A descriptive label for the current emotional or informational state.
    # Example: "listening", "thinking", "curious", "error"
    mood: str = "neutral"

# --- State Management ---

# The global, singleton instance of the AuroraState.
_aurora_state_instance = AuroraState()

def get_aurora_state() -> AuroraState:
    """Returns the singleton instance of the AuroraState."""
    return _aurora_state_instance

def update_aurora_state(intensity: float = None, pulse_speed: float = None, 
                        temperature: float = None, mood: str = None):
    """
    Updates the global AuroraState with new values.
    Only non-None parameters will update the state.
    """
    global _aurora_state_instance
    
    if intensity is not None:
        _aurora_state_instance.intensity = max(0.0, min(1.0, intensity))
        
    if pulse_speed is not None:
        _aurora_state_instance.pulse_speed = max(0.5, min(2.0, pulse_speed))
        
    if temperature is not None:
        _aurora_state_instance.temperature = max(0.0, min(1.0, temperature))
        
    if mood is not None:
        _aurora_state_instance.mood = mood

    # Optionally, you could add a signal emission here if other parts
    # of the application need to react to state changes immediately.
    # For example: from corund.signals import signal_bus
    # signal_bus.aurora_state_changed.emit()

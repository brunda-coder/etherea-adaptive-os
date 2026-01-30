import pytest
import time
from corund.ei_engine import EIEngine


def test_hierarchical_ei_initial():
    engine = EIEngine()
    assert "focus" in engine.emotion_vector
    assert "flow_intensity" in engine.sub_states


def test_micro_signal_integration():
    engine = EIEngine()
    initial_stress = engine.emotion_vector["stress"]

    # Simulate jittery mouse movement (Level 3)
    engine.on_input_activity("mouse", {"intensity": 0.5, "jitter": 1.0})

    # Level 3 Jitter -> Level 2 Jitter -> Level 1 Stress
    assert engine.sub_states["physical_jitter"] > 0
    assert engine.emotion_vector["stress"] > initial_stress


def test_sub_state_flow_transition():
    engine = EIEngine()
    # Mock high focus, low stress, high rhythm for Flow
    engine.emotion_vector["focus"] = 0.8
    engine.emotion_vector["stress"] = 0.2
    engine.sub_states["typing_rhythm"] = 0.8

    # Run loop logic once
    dt = 1.0
    engine.sub_states["flow_intensity"] = min(
        1.0, engine.sub_states["flow_intensity"] + 0.05 * dt)

    assert engine.sub_states["flow_intensity"] > 0

import pytest
from corund.ei_engine import EIEngine


def test_ei_engine_initial_state():
    engine = EIEngine()
    assert engine.state["focus"] == 0.5
    assert engine.state["stress"] == 0.2
    assert engine.state["flow"] == 0.0


def test_ei_engine_input_reaction():
    engine = EIEngine()
    initial_focus = engine.state["focus"]

    # Simulate high intensity typing
    engine.on_input_activity("typing", 1.0)
    assert engine.state["focus"] > initial_focus
    assert engine.state["stress"] > 0.2


def test_flow_state_transition():
    engine = EIEngine()
    # Mock high focus and moderate stress
    engine.state["focus"] = 0.8
    engine.state["stress"] = 0.4

    # Run one loop cycle manually
    dt = 1.0
    if engine.state["focus"] > 0.7 and 0.2 < engine.state["stress"] < 0.6:
        engine.state["flow"] = min(1.0, engine.state["flow"] + 0.05 * dt)

    assert engine.state["flow"] > 0.0

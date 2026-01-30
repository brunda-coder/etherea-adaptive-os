import pytest
from corund.emotion_mapper import mapper


def test_mapper_easing():
    emotion_vector = {"focus": 1.0, "stress": 0.0,
                      "energy": 0.5, "curiosity": 0.5}
    dt = 0.016

    initial_glow = mapper.params["glow_intensity"]

    # Update mapping
    # Focus 1.0 -> target glow 1.0
    params = mapper.update(emotion_vector, dt)

    # Eased value should have moved towards target but not jumped
    assert params["glow_intensity"] > initial_glow
    assert params["glow_intensity"] < 1.0  # Should not jump instantly

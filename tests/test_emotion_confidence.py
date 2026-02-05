from core.emotion.emotion_engine import EmotionEngine


def test_emotion_confidence_gating():
    engine = EmotionEngine()
    engine.record_typing(0.9, 0.1)
    engine.record_error(0.7)
    state = engine.tick()

    assert state.confidence > 0.0
    assert "frustrated" in state.probabilities

    engine.set_kill_switch(True)
    disabled = engine.tick()
    assert disabled.confidence == 0.0
    assert disabled.probabilities.get("neutral") == 1.0

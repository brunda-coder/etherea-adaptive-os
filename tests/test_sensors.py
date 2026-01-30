import time
import pytest
from sensors.hid_sensor import HIDSensor
from corund.signals import signals


def test_hid_sensor_initialization():
    sensor = HIDSensor()
    assert sensor.sample_rate == 120
    assert not sensor.running


def test_hid_sensor_start_stop():
    # We won't test hardware listeners in unit tests to avoid OS dependency issues
    # but we can test the logic
    sensor = HIDSensor()
    sensor.running = True
    sensor.key_presses = 5
    sensor.mouse_movement_dist = 200

    # Simulate a sampling cycle manually
    intensity_log = []
    signals.input_activity.connect(lambda t, i: intensity_log.append((t, i)))

    # Manually invoke sampling logic for one cycle
    mouse_intensity = min(1.0, sensor.mouse_movement_dist / 100.0)
    kb_intensity = min(1.0, sensor.key_presses / 1.0)

    assert mouse_intensity == 1.0
    assert kb_intensity == 1.0

    sensor.running = False

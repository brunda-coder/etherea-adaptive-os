import time
import threading
try:
    import numpy as np
except Exception:
    np = None  # optional on Termux/CI
from pynput import mouse, keyboard
from corund.signals import signals


class HIDSensor:
    """
    High-frequency (120Hz target) HID sensor integration.
    Monitors keyboard and mouse activity to quantify 'intensity' and 'velocity'.
    """

    def __init__(self):
        self.running = False

        # Activity counters / accumulators
        self.key_presses = 0
        self.last_key_time = time.time()
        self.key_intervals = []  # For variance check

        self.mouse_movement_dist = 0
        self.last_mouse_pos = (0, 0)
        self.mouse_velocities = []  # For jitter check

        # Sampling state
        self.sample_rate = 120  # Hz
        self.interval = 1.0 / self.sample_rate

        # Listeners
        self.mouse_listener = None
        self.kb_listener = None

    def start(self):
        self.running = True

        # Start HW listeners
        self.mouse_listener = mouse.Listener(on_move=self._on_mouse_move)
        self.kb_listener = keyboard.Listener(on_press=self._on_key_press)

        self.mouse_listener.start()
        self.kb_listener.start()

        # Start sampling loop
        threading.Thread(target=self._sampling_loop, daemon=True).start()

    def stop(self):
        self.running = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.kb_listener:
            self.kb_listener.stop()

    def _on_mouse_move(self, x, y):
        now = time.time()
        dx = x - self.last_mouse_pos[0]
        dy = y - self.last_mouse_pos[1]
        dist = (dx**2 + dy**2)**0.5
        self.mouse_movement_dist += dist

        # Track velocity for jitter analysis
        if dist > 0:
            self.mouse_velocities.append(dist)

        self.last_mouse_pos = (x, y)

    def _on_key_press(self, key):
        now = time.time()
        dt = now - self.last_key_time
        self.key_intervals.append(dt)
        self.last_key_time = now
        self.key_presses += 1

    def _sampling_loop(self):
        while self.running:
            start_time = time.time()

            # 1. Process Mouse Activity
            mouse_velocity = self.mouse_movement_dist / self.interval
            mouse_intensity = min(1.0, self.mouse_movement_dist / 100.0)

            # calculate jitter (variance in velocity)
            jitter = 0
            if len(self.mouse_velocities) > 1:
                jitter = float(np.std(self.mouse_velocities))

            if self.mouse_movement_dist > 0:
                # Structured event with micro-signals
                signals.input_activity.emit("mouse", {
                    "intensity": mouse_intensity,
                    "jitter": min(1.0, jitter / 50.0)
                })

            # 2. Process Keyboard Activity
            kb_intensity = min(1.0, self.key_presses / 1.0)
            typing_variance = 0
            if len(self.key_intervals) > 1:
                typing_variance = float(np.std(self.key_intervals))

            if self.key_presses > 0:
                signals.input_activity.emit("typing", {
                    "intensity": kb_intensity,
                    "variance": min(1.0, typing_variance * 5.0)
                })

            # Reset accumulators
            self.mouse_movement_dist = 0
            self.key_presses = 0
            self.key_intervals = []
            self.mouse_velocities = []

            # Sleep to maintain 120Hz
            elapsed = time.time() - start_time
            sleep_time = max(0, self.interval - elapsed)
            time.sleep(sleep_time)


# Global Instance
hid_sensor = HIDSensor()

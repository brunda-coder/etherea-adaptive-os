from pynput import keyboard
from corund.signals import signals
import time
import threading


class KeyboardSensor:
    def __init__(self):
        self.listener = None
        self.last_type_time = 0

    def start(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()

    def on_press(self, key):
        now = time.time()
        # Calculate typing speed intensity (simplified)
        dt = now - self.last_type_time
        intensity = min(1.0, 1.0 / (dt + 0.1)) if dt > 0 else 0.5

        signals.input_activity.emit("typing", intensity)
        self.last_type_time = now

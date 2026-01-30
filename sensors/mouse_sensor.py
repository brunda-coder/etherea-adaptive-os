from pynput import mouse
from corund.signals import signals
import time
import math
try:
    import numpy as np
except Exception:
    np = None  # optional on Termux/CI


class MouseSensor:
    def __init__(self):
        self.listener = None
        self.last_pos = (0, 0)
        self.last_move_time = 0

    def start(self):
        self.listener = mouse.Listener(on_move=self.on_move)
        self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()

    def on_move(self, x, y):
        now = time.time()
        dt = now - self.last_move_time
        if dt > 0.05:  # throttle updates
            # Calculate velocity/intensity
            dist = math.hypot(x - self.last_pos[0], y - self.last_pos[1])
            intensity = min(1.0, dist / 100.0)

            signals.input_activity.emit("mouse", intensity)

            self.last_pos = (x, y)
            self.last_move_time = now

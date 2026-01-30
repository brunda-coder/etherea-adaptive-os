import threading
import time
try:
    from PySide6.QtCore import QObject, Signal
except Exception:
    class QObject:  # minimal stub
        pass
    def Signal(*a, **k):
        return None
try:
    from pynput import mouse, keyboard
except ImportError:
    mouse = None
    keyboard = None

class InputSenses(QObject):
    """
    Senses user activity (Mouse/Keyboard) to determine 'Focus' or 'Idle' states.
    Privacy First: Counts events only. Does NOT log keys or positions.
    """
    activity_level_changed = Signal(float)  # 0.0 (idle) to 1.0 (intense)
    pattern_detected = Signal(dict) # {"hesitation": bool, "repetition": bool, "late_night": bool}

    def __init__(self):
        super().__init__()
        self._apm = 0  
        self._last_event_time = time.time()
        self._running = False
        
        # Counters for current second
        self._events_this_frame = 0
        self._event_history = [] # Last 10 event types
        
        if not mouse or not keyboard:
            print("[InputSenses] pynput not installed. Sensing disabled.")
            return

        self._mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        self._key_listener = keyboard.Listener(
            on_press=self._on_press
        )
        
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)

    def start(self):
        if not mouse: return
        self._running = True
        self._mouse_listener.start()
        self._key_listener.start()
        self._monitor_thread.start()

    def stop(self):
        self._running = False
        if mouse:
            self._mouse_listener.stop()
            self._key_listener.stop()

    def _record_event(self, type_name: str, intensity: float):
        self._events_this_frame += intensity
        self._last_event_time = time.time()
        self._event_history.append(type_name)
        if len(self._event_history) > 10:
            self._event_history.pop(0)

    def _on_move(self, x, y):
        self._record_event("move", 0.5)

    def _on_click(self, x, y, button, pressed):
        if pressed: self._record_event("click", 2.0)

    def _on_scroll(self, x, y, dx, dy):
        self._record_event("scroll", 1.0)

    def _on_press(self, key):
        type_name = "key"
        try:
            if key == keyboard.Key.backspace or key == keyboard.Key.delete:
                type_name = "delete"
        except: pass
        self._record_event(type_name, 1.5)

    def _monitor_loop(self):
        """Calculates 'Energy' and 'Patterns' as per Etherea Manifest."""
        while self._running:
            time.sleep(1.0)
            now = time.time()
            
            # 1. Energy Calculation
            current_energy = min(1.0, self._events_this_frame / 20.0)
            self._events_this_frame = 0
            
            # 2. Pattern: Hesitation (Idle)
            idle_time = now - self._last_event_time
            hesitation = 5.0 < idle_time < 300.0
            
            # 3. Pattern: Repetition
            repetition = False
            if len(self._event_history) >= 5:
                last_5 = self._event_history[-5:]
                repetition = all(x == last_5[0] for x in last_5)

            # 4. Pattern: Deletions (Micro-Hesitation)
            deletions = self._event_history.count("delete")
            
            # 5. Pattern: Late Night
            from datetime import datetime
            hour = datetime.now().hour
            late_night = (hour >= 22 or hour < 5)

            # Update signals
            self.activity_level_changed.emit(current_energy)
            self.pattern_detected.emit({
                "hesitation": hesitation,
                "repetition": repetition,
                "deletions": deletions,
                "late_night": late_night
            })

            # Clean history gradually
            if len(self._event_history) > 20:
                self._event_history = self._event_history[-10:]

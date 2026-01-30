import time
try:
    from PySide6.QtCore import QObject, Signal
except Exception:
    class QObject:  # minimal stub
        pass
    def Signal(*a, **k):
        return None

class AppState(QObject):
    """
    Single source of truth for the application state.
    Manages 'mode' (idle/focus/break) and EI metrics (focus/stress/energy/curiosity).
    """
    mode_changed = Signal(str)  # mode
    ei_updated = Signal(dict)   # full vector

    _instance = None

    def __init__(self):
        super().__init__()
        self._mode = "idle"
        self._ei = {
            "focus": 0.5,
            "stress": 0.2,
            "energy": 0.5,
            "curiosity": 0.5
        }
        self._expressive_mode = "idle"
        self._updated_at = time.time()

    @property
    def expressive_mode(self) -> str:
        return self._expressive_mode

    def set_expressive_mode(self, mode: str):
        if self._expressive_mode != mode:
            self._expressive_mode = mode
            self.ei_updated.emit(self._ei) # Trigger UI update

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = AppState()
        return cls._instance

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def ei(self) -> dict:
        return self._ei.copy()

    @property
    def stress(self) -> float:
        return self._ei.get("stress", 0.5)

    @property
    def energy(self) -> float:
        return self._ei.get("energy", 0.5)

    @property
    def focus(self) -> float:
        return self._ei.get("focus", 0.5)

    def set_mode(self, mode: str, reason: str = ""):
        valid_modes = {"idle", "focus", "break"}
        mode = mode.lower().strip()
        if mode not in valid_modes:
            print(f"⚠️ Invalid mode requested: {mode}")
            return
        
        if self._mode != mode:
            self._mode = mode
            self._updated_at = time.time()
            self.mode_changed.emit(mode)
            print(f"State Mode -> {mode} ({reason})")

    def update_ei(self, **metrics):
        """
        Update one or more EI metrics. Values clamped 0.0 to 1.0.
        Example: state.update_ei(focus=0.8, stress=0.1)
        """
        changed = False
        for k, v in metrics.items():
            if k in self._ei:
                # clamp
                val = max(0.0, min(1.0, float(v)))
                if abs(self._ei[k] - val) > 0.001:
                    self._ei[k] = val
                    changed = True
        
        if changed:
            self.ei_updated.emit(self._ei)

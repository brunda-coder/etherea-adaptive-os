import threading
import time
import math
import random
try:
    from PySide6.QtCore import QObject, Signal
except Exception:
    class QObject:  # minimal stub
        pass
    def Signal(*a, **k):
        return None

class MusicEngine(QObject):
    """
    Simulates a music player and generates synthetic Audio Spectrum Data.
    Emits signals for Bass, Mids, and Highs to drive UI animations.
    """
    spectrum_updated = Signal(dict) # { 'bass': float, 'mid': float, 'high': float }
    track_changed = Signal(str)
    playback_state_changed = Signal(bool) # True=Playing

    _instance = None

    def __init__(self):
        super().__init__()
        self._is_playing = False
        self._track_name = ""
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = MusicEngine()
        return cls._instance

    def play(self, track_name: str = "Etherea Ambient Mix"):
        self._track_name = track_name
        self._is_playing = True
        self.track_changed.emit(track_name)
        self.playback_state_changed.emit(True)

    def stop(self):
        self._is_playing = False
        self.playback_state_changed.emit(False)

    def _run_loop(self):
        t = 0.0
        while True:
            if self._is_playing:
                t += 0.05
                
                # Synthetic Audio Reactivity simulation
                # Bass: Slow, heavy beat (approx 120bpm)
                beat = (math.sin(t * 12.0) + 1.0) * 0.5
                bass = beat * beat * beat # Sharper peaks
                if bass < 0.1: bass = 0.0
                
                # Mids: Melody/Vocals (Complex wave)
                mid = (math.sin(t * 5.0) * math.cos(t * 3.0) + 1.0) * 0.4
                mid += random.random() * 0.2
                
                # Highs: Hi-hats/Atmosphere (Fast noise)
                high = random.random() * 0.4 + (0.3 if beat > 0.8 else 0.0)
                
                self.spectrum_updated.emit({
                    'bass': min(1.0, bass),
                    'mid': min(1.0, mid),
                    'high': min(1.0, high)
                })
                
            else:
                # Silence
                try:
                    self.spectrum_updated.emit({'bass':0, 'mid':0, 'high':0})
                except RuntimeError:
                    pass # App likely closing
                
            time.sleep(0.05) # 20fps updates for visuals

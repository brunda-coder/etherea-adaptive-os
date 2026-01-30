import os
import threading
import time

try:
    import pygame
except Exception:
    pygame = None


class AudioEngine:
    """
    Background audio engine for Etherea.
    - Works on Windows + Linux (AppImage)
    - Plays looping WAV/MP3 using pygame mixer
    """

    def __init__(self):
        self._thread = None
        self._stop_flag = threading.Event()
        self._is_playing = False
        self._volume = 0.5

        # Default track (you can change later)
        self.default_track = os.path.join("core", "assets", "audio", "etherea_theme_a.wav")

    def set_volume(self, vol: float):
        self._volume = max(0.0, min(1.0, float(vol)))
        if pygame:
            try:
                pygame.mixer.music.set_volume(self._volume)
            except Exception:
                pass

    def start(self, track_path: str | None = None, loop: bool = True):
        if self._is_playing:
            return

        if pygame is None:
            print("[AudioEngine] pygame not installed, audio disabled.")
            return

        track = track_path or self.default_track

        def _runner():
            try:
                pygame.mixer.init()
                pygame.mixer.music.set_volume(self._volume)

                if not os.path.exists(track):
                    print(f"[AudioEngine] Track not found: {track}")
                    return

                pygame.mixer.music.load(track)
                pygame.mixer.music.play(-1 if loop else 0)

                self._is_playing = True
                while not self._stop_flag.is_set():
                    time.sleep(0.2)

            except Exception as e:
                print("[AudioEngine] Error:", e)
            finally:
                try:
                    if pygame:
                        pygame.mixer.music.stop()
                        pygame.mixer.quit()
                except Exception:
                    pass
                self._is_playing = False
                self._stop_flag.clear()

        self._thread = threading.Thread(target=_runner, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_flag.set()

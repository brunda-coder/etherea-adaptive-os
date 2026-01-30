from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import json


@dataclass
class MotionCommand:
    action: str            # "play_motion"
    clip: str              # e.g., "dance_hype_01"
    intensity: float = 1.0 # 0.5 - 2.0
    loop: bool = True
    duration: float = 0.0  # optional seconds (0 = runtime decides)


class AvatarMotionController:
    """
    Motion Controller (Phase-1 stub)
    - Does NOT require PySide6 / OpenAI / installs
    - Logs motion requests safely
    - Later: will send commands to Unity/Unreal runtime via localhost bridge
    """

    def __init__(self, catalog_path: str = "core/avatar_motion/motion_catalog.json"):
        self.catalog_path = Path(catalog_path)
        self.catalog: Dict[str, Any] = {}
        self.last_command: Optional[MotionCommand] = None
        self.load_catalog()

    def load_catalog(self) -> None:
        try:
            self.catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        except Exception:
            self.catalog = {}

    def has_clip(self, clip: str) -> bool:
        # scan all lists in catalog
        if not self.catalog:
            return False
        for k, v in self.catalog.items():
            if isinstance(v, list) and clip in v:
                return True
            if isinstance(v, dict):
                for _, vv in v.items():
                    if isinstance(vv, list) and clip in vv:
                        return True
        return False

    def choose_emotion_idle(self, emotion: str) -> str:
        emo = (emotion or "calm").lower()
        emotion_map = self.catalog.get("emotion", {}) if isinstance(self.catalog.get("emotion"), dict) else {}
        clips = emotion_map.get(emo) or emotion_map.get("calm") or ["idle_breathe_01"]
        return clips[0]

    def play(self, clip: str, intensity: float = 1.0, loop: bool = True, duration: float = 0.0) -> MotionCommand:
        clip = (clip or "").strip()
        if not clip:
            clip = "idle_breathe_01"

        if self.catalog and not self.has_clip(clip):
            # fallback: safe idle
            clip = "idle_breathe_01"

        cmd = MotionCommand(action="play_motion", clip=clip, intensity=float(intensity), loop=bool(loop), duration=float(duration))
        self.last_command = cmd
        self._log_command(cmd)
        return cmd

    def _log_command(self, cmd: MotionCommand) -> None:
        # lightweight log file (works everywhere)
        try:
            Path("etherea_motion.log").write_text(
                f"action={cmd.action} clip={cmd.clip} intensity={cmd.intensity} loop={cmd.loop} duration={cmd.duration}\n",
                encoding="utf-8"
            )
        except Exception:
            pass
        print(f"🎬 MotionRequest -> {cmd.clip} (intensity={cmd.intensity}, loop={cmd.loop})")

    def play_dance(self, duration_s: float = 15.0, bpm: float = 120.0, style: str = "bolly_pop", energy: float = 1.2):
        """Generate an original dance routine timeline and log it."""
        from corund.avatar_motion.dance_planner import generate_beat_grid, build_original_dance_timeline

        beats = generate_beat_grid(duration_s=duration_s, bpm=bpm)
        timeline = build_original_dance_timeline(beats, style=style, energy=energy)

        # Log the routine (Phase-1)
        try:
            Path("etherea_dance_timeline.json").write_text(__import__("json").dumps(timeline, indent=2), encoding="utf-8")
        except Exception:
            pass

        print(f"💃 DanceRoutine -> style={style} bpm={bpm} duration={duration_s}s steps={len(timeline)}")
        return timeline

    def play_dance_to_song(self, wav_path: str, style: str = "bolly_pop", energy: float = 1.25):
        """Generate original routine synced to real beat timings from a WAV song."""
        from corund.audio_analysis.beat_detector import estimate_bpm_and_beats
        from corund.avatar_motion.dance_planner import build_original_dance_timeline

        bpm, beats = estimate_bpm_and_beats(wav_path)

        # convert BeatPoint -> DanceBeat-like dicts
        beat_objs = []
        for b in beats:
            beat_objs.append(type("DanceBeat", (), {"t": b.t, "strength": b.strength})())

        timeline = build_original_dance_timeline(beat_objs, style=style, energy=energy)

        # Save timeline
        try:
            Path("etherea_dance_timeline_song.json").write_text(__import__("json").dumps({
                "song": wav_path,
                "bpm": bpm,
                "style": style,
                "steps": timeline
            }, indent=2), encoding="utf-8")
        except Exception:
            pass

        print(f"🎧💃 DanceToSong -> bpm={bpm} beats={len(beats)} style={style}")
        return bpm, timeline


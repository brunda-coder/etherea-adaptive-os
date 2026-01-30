from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
import random


@dataclass
class DanceBeat:
    t: float          # seconds from start
    strength: float   # 0.0 - 1.0 (downbeat stronger)


def generate_beat_grid(duration_s: float = 20.0, bpm: float = 120.0) -> List[DanceBeat]:
    """
    Termux-safe placeholder beat grid.
    Later we will replace this with real beat detection (desktop only).
    """
    beat_interval = 60.0 / max(bpm, 1.0)
    beats: List[DanceBeat] = []
    t = 0.0
    beat_count = 0

    while t <= duration_s:
        # Strong downbeat every 4 beats
        strength = 1.0 if (beat_count % 4 == 0) else 0.55
        beats.append(DanceBeat(t=t, strength=strength))
        t += beat_interval
        beat_count += 1

    return beats


def build_original_dance_timeline(
    beats: List[DanceBeat],
    style: str = "bolly_pop",
    energy: float = 1.2,
) -> List[Dict[str, Any]]:
    """
    Builds an original dance routine timeline.
    - Does NOT copy any external choreo
    - Chooses from a motion vocabulary + uses beat strengths
    """
    rng = random.Random()

    # Motion vocabulary (we'll expand later)
    base_moves = [
        "dance_hype_01",
        "dance_hype_02",
        "step_left_01",
        "step_right_01",
        "arm_wave_01",
        "hip_sway_01",
        "turn_spin_01",
        "bounce_loop_01",
        "pose_hit_01",
        "pose_hit_02",
    ]

    # Style tuning (still original)
    if style == "bolly_pop":
        preferred = ["hip_sway_01", "arm_wave_01", "pose_hit_01", "turn_spin_01"]
    elif style == "street_hype":
        preferred = ["bounce_loop_01", "pose_hit_02", "dance_hype_02"]
    else:
        preferred = ["dance_hype_01", "pose_hit_01"]

    timeline: List[Dict[str, Any]] = []
    last_clip = None

    for b in beats:
        # Choose clip on stronger beats
        if b.strength >= 0.9:
            clip = rng.choice(preferred + ["pose_hit_01", "pose_hit_02"])
            intensity = min(2.0, energy + 0.2)
            loop = False
        else:
            # Light beats get flow moves
            pool = base_moves + preferred
            clip = rng.choice(pool)
            intensity = min(2.0, max(0.7, energy))
            loop = True

        # Avoid repeating exact same clip
        if clip == last_clip:
            clip = rng.choice(base_moves)

        timeline.append({
            "t": round(b.t, 3),
            "action": "play_motion",
            "clip": clip,
            "intensity": round(float(intensity), 2),
            "loop": bool(loop),
        })
        last_clip = clip

    return timeline

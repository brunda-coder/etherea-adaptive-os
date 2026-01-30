from dataclasses import dataclass
from typing import Dict, Tuple


Color = Tuple[int, int, int]


@dataclass(frozen=True)
class AvatarSpec:
    key: str
    name: str

    # Palette
    bg_a: Color
    bg_b: Color
    ring: Color
    core: Color
    particle: Color

    # Motion tuning
    drift_speed: float      # background drift speed
    pulse_speed: float      # glow pulse speed
    particle_rate: float    # particles per second


AVATARS: Dict[str, AvatarSpec] = {
    "aurora": AvatarSpec(
        key="aurora",
        name="Aurora",
        bg_a=(18, 12, 30),
        bg_b=(10, 18, 40),
        ring=(160, 120, 255),
        core=(255, 210, 120),
        particle=(190, 170, 255),
        drift_speed=0.65,
        pulse_speed=1.10,
        particle_rate=24.0,
    ),
    "ethera": AvatarSpec(
        key="ethera",
        name="Ethera",
        bg_a=(10, 12, 22),
        bg_b=(22, 12, 30),
        ring=(120, 220, 255),
        core=(120, 255, 210),
        particle=(120, 220, 255),
        drift_speed=0.85,
        pulse_speed=1.35,
        particle_rate=30.0,
    ),
    "sentinel": AvatarSpec(
        key="sentinel",
        name="Sentinel",
        bg_a=(8, 8, 12),
        bg_b=(18, 10, 16),
        ring=(255, 120, 160),
        core=(255, 140, 90),
        particle=(255, 120, 160),
        drift_speed=0.55,
        pulse_speed=0.95,
        particle_rate=18.0,
    ),
  }

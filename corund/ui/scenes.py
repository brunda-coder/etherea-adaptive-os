from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenePreset:
    name: str
    ui_density: str
    aurora_intensity: str
    avatar_frequency: str
    signature_moment: str
    quick_actions: list[str]


SCENE_PRESETS = [
    ScenePreset(
        name="Student / Exam Prep",
        ui_density="standard",
        aurora_intensity="calm",
        avatar_frequency="low",
        signature_moment="Soft study glow + chime",
        quick_actions=["Start Focus", "Plan Today", "Calm Reset"],
    ),
    ScenePreset(
        name="Developer / Deep Work",
        ui_density="minimal",
        aurora_intensity="focus",
        avatar_frequency="silent",
        signature_moment="Code pulse sweep",
        quick_actions=["Start Focus", "Open Notes", "Silence"],
    ),
    ScenePreset(
        name="Creator / Flow",
        ui_density="rich",
        aurora_intensity="energetic",
        avatar_frequency="medium",
        signature_moment="Color bloom + whoosh",
        quick_actions=["Moodboard", "Capture Idea", "Start Focus"],
    ),
    ScenePreset(
        name="Professional / Meetings",
        ui_density="standard",
        aurora_intensity="steady",
        avatar_frequency="low",
        signature_moment="Calendar lock-in",
        quick_actions=["Start Meeting", "Recap", "Mute"],
    ),
    ScenePreset(
        name="Calm / Recovery",
        ui_density="minimal",
        aurora_intensity="calm",
        avatar_frequency="silent",
        signature_moment="Slow breathing pulse",
        quick_actions=["Calm Reset", "Breathing", "Journal"],
    ),
    ScenePreset(
        name="Beginner / Guided Mode",
        ui_density="standard",
        aurora_intensity="gentle",
        avatar_frequency="medium",
        signature_moment="Welcome shimmer",
        quick_actions=["Start Focus", "Plan Today", "Help"],
    ),
    ScenePreset(
        name="Neurodiverse / Low-Stim Focus",
        ui_density="minimal",
        aurora_intensity="steady",
        avatar_frequency="silent",
        signature_moment="Dimmed halo settle",
        quick_actions=["Low Stim", "Start Focus", "Quiet Mode"],
    ),
]

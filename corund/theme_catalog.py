from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GradientTheme:
    name: str
    stops: tuple[str, str, str]


def built_in_themes() -> list[GradientTheme]:
    themes: list[GradientTheme] = []
    for idx in range(1, 51):
        themes.append(
            GradientTheme(
                name=f"Theme {idx:02d}",
                stops=(
                    f"hsl({(idx * 7) % 360} 88% 68%)",
                    f"hsl({(idx * 11) % 360} 82% 62%)",
                    f"hsl({(idx * 17) % 360} 76% 56%)",
                ),
            )
        )
    return themes


def gradient_creator(name: str, stop_a: str, stop_b: str, stop_c: str) -> GradientTheme:
    return GradientTheme(name=name, stops=(stop_a, stop_b, stop_c))

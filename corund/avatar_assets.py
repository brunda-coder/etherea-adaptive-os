from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ALLOWED_ROOTS = ("assets", "core/assets", "corund/assets")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
MODEL_SUFFIXES = {".gltf", ".glb", ".obj", ".fbx", ".bin"}
SPRITE_SUFFIXES = {".json", ".atlas"}


@dataclass(frozen=True)
class AvatarAssetManifest:
    images: list[Path]
    sprites: list[Path]
    models: list[Path]

    @property
    def total_count(self) -> int:
        return len(self.images) + len(self.sprites) + len(self.models)


class AvatarAssetManifestLoader:
    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or Path(__file__).resolve().parents[1]

    def _iter_files(self, roots: Iterable[str]) -> Iterable[Path]:
        for root in roots:
            base = self.repo_root / root
            if not base.exists():
                continue
            for f in base.rglob("*"):
                if f.is_file() and "avatar" in str(f).lower():
                    yield f

    def load(self) -> AvatarAssetManifest:
        images: list[Path] = []
        sprites: list[Path] = []
        models: list[Path] = []
        for f in self._iter_files(ALLOWED_ROOTS):
            ext = f.suffix.lower()
            rel = f.relative_to(self.repo_root)
            if ext in IMAGE_SUFFIXES:
                images.append(rel)
            elif ext in MODEL_SUFFIXES:
                models.append(rel)
            elif ext in SPRITE_SUFFIXES:
                sprites.append(rel)
        return AvatarAssetManifest(sorted(images), sorted(sprites), sorted(models))


def required_avatar_assets_missing(repo_root: Path | None = None) -> list[str]:
    root = repo_root or Path(__file__).resolve().parents[1]
    required = [
        "assets/avatar/face_idle.webp",
        "corund/assets/avatar_hero/base.png",
        "assets/avatar_hero/avatar_full_body.png",
    ]
    return [p for p in required if not (root / p).exists()]

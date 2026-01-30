from __future__ import annotations
from pathlib import Path

from corund.app_runtime import user_data_dir


CACHE_DIR = user_data_dir() / "music_cache"


def ensure_cache_dir() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR


def safe_slug(name: str) -> str:
    name = (name or "").strip().lower()
    keep = []
    for ch in name:
        if ch.isalnum() or ch in ("-", "_"):
            keep.append(ch)
        elif ch.isspace():
            keep.append("_")
    out = "".join(keep).strip("_")
    return out[:80] if out else "song"


def cached_song_path(song_name: str, ext: str = "wav") -> Path:
    ensure_cache_dir()
    return CACHE_DIR / f"{safe_slug(song_name)}.{ext}"


def find_cached(song_name: str):
    """
    Returns cached file path if exists (.wav preferred).
    """
    ensure_cache_dir()
    slug = safe_slug(song_name)

    # prefer wav
    wav = CACHE_DIR / f"{slug}.wav"
    if wav.exists():
        return wav

    mp3 = CACHE_DIR / f"{slug}.mp3"
    if mp3.exists():
        return mp3

    # fallback: any file containing slug
    for p in CACHE_DIR.glob("*"):
        if slug in p.name.lower():
            return p

    return None

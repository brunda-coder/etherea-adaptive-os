from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple
import os

try:
    import requests
except Exception:
    requests = None  # optional on Termux/CI

from corund.audio_analysis.song_cache import find_cached, cached_song_path, ensure_cache_dir


DEFAULT_LOCAL_DIRS = [
    "/sdcard/Music",
    "/sdcard/Download",
    str(Path.home() / "Music"),
    str(Path.home() / "Downloads"),
]


def search_local(song_name: str, exts=(".wav", ".mp3")) -> Optional[Path]:
    """
    Search common folders for a song that matches name (case-insensitive).
    """
    name = (song_name or "").strip().lower()
    if not name:
        return None

    dirs = list(DEFAULT_LOCAL_DIRS)

    # allow override from env (comma-separated)
    extra = os.environ.get("ETHEREA_MUSIC_DIRS", "")
    if extra.strip():
        dirs.extend([d.strip() for d in extra.split(",") if d.strip()])

    for d in dirs:
        base = Path(d).expanduser()
        if not base.exists():
            continue

        try:
            for p in base.rglob("*"):
                if p.is_file() and p.suffix.lower() in exts:
                    if name in p.stem.lower():
                        return p
        except Exception:
            continue

    return None


def download_to_cache(song_name: str, url: str) -> Path:
    """
    Download from a DIRECT URL into cache (safe/legal).
    """
    ensure_cache_dir()
    target = cached_song_path(song_name, ext="wav")

    # infer extension if URL ends with .mp3 etc
    lower = (url or "").lower()
    if lower.endswith(".mp3"):
        target = cached_song_path(song_name, ext="mp3")
    elif lower.endswith(".wav"):
        target = cached_song_path(song_name, ext="wav")

    r = requests.get(url, stream=True, timeout=30)
    r.raise_for_status()

    with open(target, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 256):
            if chunk:
                f.write(chunk)

    return target


def resolve_song(song_name: str, url: Optional[str] = None) -> Tuple[Optional[Path], str]:
    """
    Resolve song path using:
    1) cache
    2) local search
    3) direct URL download (if provided)
    Returns: (path_or_none, status_message)
    """
    # 1) cache
    cached = find_cached(song_name)
    if cached:
        return Path(cached), "cache"

    # 2) local search
    local = search_local(song_name)
    if local:
        return Path(local), "local"

    # 3) URL download (safe only if user provides URL)
    if url and url.strip():
        try:
            p = download_to_cache(song_name, url.strip())
            return p, "downloaded"
        except Exception as e:
            return None, f"download_failed: {e}"

    return None, "not_found"

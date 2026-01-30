from __future__ import annotations

import os
import shutil
import tempfile
import subprocess
from pathlib import Path


def _has_cmd(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _play_audio_file(path: str) -> bool:
    """
    Best-effort playback across environments.
    Returns True if playback likely started.
    """
    p = str(path)

    # 1) playsound (if installed)
    try:
        import playsound  # type: ignore
        playsound.playsound(p)
        return True
    except Exception:
        pass

    # 2) Windows: PowerShell MediaPlayer
    if os.name == "nt":
        try:
            ps = [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "$p = '" + p.replace("'", "''") + "';"
                    "Add-Type -AssemblyName presentationCore;"
                    "$m = New-Object System.Windows.Media.MediaPlayer;"
                    "$m.Open([Uri]$p);"
                    "$m.Volume = 1.0;"
                    "$m.Play();"
                    "Start-Sleep -Milliseconds 200;"
                    "while($m.NaturalDuration.HasTimeSpan -and $m.Position -lt $m.NaturalDuration.TimeSpan) { Start-Sleep -Milliseconds 200 }"
                ),
            ]
            subprocess.run(ps, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            pass

    # 3) Linux/macOS: ffplay
    if _has_cmd("ffplay"):
        try:
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", p],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception:
            pass

    # 4) Linux: aplay for wav
    if p.lower().endswith(".wav") and _has_cmd("aplay"):
        try:
            subprocess.run(["aplay", "-q", p], check=False)
            return True
        except Exception:
            pass

    return False




def _get_openai_key() -> str | None:
    # Support both standard and the user's GitHub secret name.
    return os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY2")


def speak_openai_tts(
    text: str,
    *,
    voice: str = "breeze",
    model: str | None = None,
    instructions: str | None = None,
    fmt: str = "mp3",
    speed: float | None = None,
) -> bool:
    """
    OpenAI TTS (best-effort).
    - Reads OPENAI_API_KEY or OPENAI_API_KEY2 from environment.
    - Writes audio to a temp file, then plays it with the best available player.

    Returns True if the request/playback likely started.
    """
    key = _get_openai_key()
    if not key:
        return False

    model = model or os.getenv("ETHEREA_OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    voice = (voice or os.getenv("ETHEREA_OPENAI_TTS_VOICE", "breeze")).strip()
    # Map ChatGPT voice names to supported API voices.
    _voices = {"alloy","ash","ballad","coral","echo","fable","onyx","nova","sage","shimmer","verse","marin","cedar"}
    _aliases = {"breeze": "marin", "breezy": "marin"}
    vlow = voice.lower()
    if vlow not in _voices:
        voice = _aliases.get(vlow, "marin")
    fmt = (fmt or "mp3").strip().lower()

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return False

    try:
        client = OpenAI(api_key=key)
        # temp output
        tmpdir = Path(tempfile.mkdtemp(prefix="etherea_tts_"))
        out = tmpdir / f"tts.{fmt}"

        # newer SDK supports with_streaming_response + stream_to_file
        created = False
        try:
            kwargs = {"model": model, "voice": voice, "input": text}
            if instructions:
                kwargs["instructions"] = instructions
            if speed is not None:
                kwargs["speed"] = float(speed)
            # Some SDKs use 'format', others 'response_format'
            try:
                kwargs["format"] = fmt
                with client.audio.speech.with_streaming_response.create(**kwargs) as resp:
                    resp.stream_to_file(str(out))
                created = True
            except TypeError:
                kwargs.pop("format", None)
                kwargs["response_format"] = fmt
                with client.audio.speech.with_streaming_response.create(**kwargs) as resp:
                    resp.stream_to_file(str(out))
                created = True
        except Exception:
            # fallback to non-streaming create (older variants)
            try:
                kwargs = {"model": model, "voice": voice, "input": text}
                if instructions:
                    kwargs["instructions"] = instructions
                if speed is not None:
                    kwargs["speed"] = float(speed)
                try:
                    kwargs["format"] = fmt
                except Exception:
                    pass
                audio = client.audio.speech.create(**kwargs)
                # audio may be bytes or have 'read' method
                data = getattr(audio, "read", None)
                if callable(data):
                    data = audio.read()
                if isinstance(data, (bytes, bytearray)):
                    out.write_bytes(data)
                    created = True
            except Exception:
                created = False

        if not created or not out.exists():
            return False

        return _play_audio_file(str(out))
    except Exception:
        return False


def speak_edge_tts(
    text: str,
    *,
    voice: str = "en-IN-NeerjaNeural",
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0st",
    ssml: bool = False,
    is_ssml: bool = False,
) -> bool:
    """
    Speak using Edge TTS (python module or CLI).
    Accepts SSML when ssml=True / is_ssml=True.
    """
    text = (text or "").strip()
    if not text:
        return False

    ssml = bool(ssml or is_ssml)

    # Try python edge-tts module first
    try:
        import asyncio
        import edge_tts  # type: ignore

        async def _run() -> str:
            tmpdir = Path(tempfile.gettempdir()) / "etherea_tts"
            tmpdir.mkdir(parents=True, exist_ok=True)
            out = tmpdir / f"etherea_tts_{abs(hash(text)) % 10_000_000}.mp3"

            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume,
                pitch=pitch,
            )
            await communicate.save(str(out))
            return str(out)

        out_path = asyncio.run(_run())
        return _play_audio_file(out_path)

    except Exception:
        pass

    # Fallback: edge-tts CLI if installed
    if _has_cmd("edge-tts"):
        try:
            tmpdir = Path(tempfile.gettempdir()) / "etherea_tts"
            tmpdir.mkdir(parents=True, exist_ok=True)
            out = tmpdir / f"etherea_tts_{abs(hash(text)) % 10_000_000}.mp3"

            cmd = [
                "edge-tts",
                "--voice", voice,
                "--rate", rate,
                "--volume", volume,
                "--pitch", pitch,
                "--text", text,
                "--write-media", str(out),
            ]
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if out.exists():
                return _play_audio_file(str(out))
            return False
        except Exception:
            return False

    return False

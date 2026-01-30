from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import wave
import struct
import math


@dataclass
class BeatPoint:
    t: float
    strength: float


def _read_wav_mono(path: str, max_seconds: float = 30.0) -> Tuple[int, List[float]]:
    """
    Read WAV file and return (sample_rate, mono_samples[-1..1]).
    Pure python, no numpy.
    """
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        n_frames = wf.getnframes()

        max_frames = int(min(n_frames, max_seconds * sr))
        raw = wf.readframes(max_frames)

    # decode PCM
    if sampwidth == 2:
        fmt = "<" + "h" * (len(raw) // 2)
        data = struct.unpack(fmt, raw)
        # mono mix
        if n_channels == 2:
            mono = [(data[i] + data[i+1]) / 2 for i in range(0, len(data), 2)]
        else:
            mono = list(data)
        # normalize
        peak = max(1, max(abs(x) for x in mono))
        samples = [x / peak for x in mono]
        return sr, samples

    raise ValueError("Only 16-bit PCM WAV supported (sampwidth=2).")


def estimate_bpm_and_beats(wav_path: str, window_ms: int = 50) -> Tuple[float, List[BeatPoint]]:
    """
    Very lightweight beat estimation:
    1) compute short-time energy envelope
    2) detect peaks
    3) estimate BPM from average peak interval
    Returns: (bpm, beats)
    """
    sr, samples = _read_wav_mono(wav_path, max_seconds=30.0)

    hop = int(sr * (window_ms / 1000.0))
    hop = max(1, hop)

    # energy envelope
    env = []
    for i in range(0, len(samples), hop):
        chunk = samples[i:i+hop]
        if not chunk:
            break
        e = sum(x*x for x in chunk) / max(1, len(chunk))
        env.append(e)

    if len(env) < 10:
        return 120.0, []

    # smooth
    smooth = []
    k = 4
    for i in range(len(env)):
        lo = max(0, i-k)
        hi = min(len(env), i+k+1)
        smooth.append(sum(env[lo:hi]) / (hi-lo))

    # dynamic threshold
    mean = sum(smooth) / len(smooth)
    thr = mean * 1.6

    # peak pick
    peaks = []
    for i in range(1, len(smooth)-1):
        if smooth[i] > thr and smooth[i] > smooth[i-1] and smooth[i] > smooth[i+1]:
            t = (i * hop) / sr
            strength = min(1.0, (smooth[i] / (thr + 1e-9)) / 2.0)
            peaks.append(BeatPoint(t=t, strength=strength))

    # if too many peaks, raise threshold
    if len(peaks) > 220:
        thr = mean * 2.2
        peaks2 = []
        for i in range(1, len(smooth)-1):
            if smooth[i] > thr and smooth[i] > smooth[i-1] and smooth[i] > smooth[i+1]:
                t = (i * hop) / sr
                strength = min(1.0, (smooth[i] / (thr + 1e-9)) / 2.0)
                peaks2.append(BeatPoint(t=t, strength=strength))
        peaks = peaks2

    # BPM estimate from median peak interval
    if len(peaks) < 4:
        return 120.0, peaks

    intervals = []
    for a, b in zip(peaks, peaks[1:]):
        dt = b.t - a.t
        if 0.2 <= dt <= 1.2:  # plausible beat interval range
            intervals.append(dt)

    if not intervals:
        return 120.0, peaks

    intervals.sort()
    med = intervals[len(intervals)//2]
    bpm = 60.0 / med

    # clamp bpm to sane range
    while bpm < 70:
        bpm *= 2
    while bpm > 190:
        bpm /= 2

    return float(round(bpm, 2)), peaks

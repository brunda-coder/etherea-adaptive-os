# core/utils.py
"""
Utility module for Etherea
- Centralized helpers for secure access to API keys (supports secrets)
- File/folder helpers and debug utilities
- Emotion-related helper functions
"""

import os

DEBUG = True  # toggle debug printing


def debug_print(label, value):
    """Print debug messages if DEBUG is True"""
    if DEBUG:
        print(f"[DEBUG] {label}: {value}")

# --- API Key Helper ---


def get_api_key(secret_key=None):
    """
    Return Etherea API key.
    Priority:
    1. secret_key argument (from GitHub secret / hosted secret)
    2. ETHEREA_API_KEY environment variable (optional fallback)
    Raises error if key not found.
    """
    if secret_key:
        return secret_key
    key = os.getenv("ETHEREA_API_KEY")
    if not key:
        raise ValueError(
            "[!] ETHEREA_API_KEY not found in secrets or environment")
    return key

# --- File / Folder Helpers ---


def ensure_folder(path):
    """Create folder if it does not exist"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        debug_print("Folder created", path)


def read_file(path):
    """Read a text file safely, returns None if not found"""
    if not os.path.exists(path):
        debug_print("read_file", f"File not found: {path}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        debug_print("read_file error", str(e))
        return None


def write_file(path, content):
    """Write content to a file safely"""
    ensure_folder(os.path.dirname(path))
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        debug_print("write_file", f"File written: {path}")
    except Exception as e:
        debug_print("write_file error", str(e))

# --- Emotional Helpers ---


def compute_emotion_score(emotion_dict):
    """Clamp intensity to 0-1"""
    return max(0.0, min(1.0, float(emotion_dict.get("intensity", 0.0))))


def merge_emotions(base_emotion, new_emotion):
    """
    Merge two emotion dictionaries
    Keeps intensity clamped 0-1
    """
    merged = base_emotion.copy()
    merged.update(new_emotion)
    merged["intensity"] = compute_emotion_score(merged)
    return merged


def emotion_to_voice_params(emotion):
    """
    Convert emotional state to TTS parameters (rate, volume)
    Supported tones: happy, sad, angry, calm, excited
    """
    tone = emotion.get("tone", "neutral")
    intensity = compute_emotion_score(emotion)
    rate = 150
    volume = 1.0

    if tone == "happy":
        rate = int(150 + 20 * intensity)
        volume = min(1.0, 0.8 + 0.2 * intensity)
    elif tone == "sad":
        rate = int(130 - 20 * intensity)
        volume = max(0.6, 0.6 - 0.1 * intensity)
    elif tone == "angry":
        rate = int(160 + 30 * intensity)
        volume = min(1.0, 0.9 + 0.1 * intensity)
    elif tone == "calm":
        rate = int(140 - 10 * intensity)
        volume = max(0.7, 0.7 - 0.05 * intensity)
    elif tone == "excited":
        rate = int(170 + 20 * intensity)
        volume = min(1.0, 0.9 + 0.1 * intensity)

    debug_print("emotion_to_voice_params", {
                "tone": tone, "rate": rate, "volume": volume})
    return {"rate": rate, "volume": volume}

# --- Extra Utilities ---


def clamp(value, min_value=0.0, max_value=1.0):
    """Clamp numeric value between min and max"""
    return max(min_value, min(max_value, value))


def merge_dicts(base, update):
    """Shallow merge two dictionaries"""
    merged = base.copy()
    merged.update(update)
    return merged

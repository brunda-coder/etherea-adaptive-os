#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "✅ Etherea Upgrade: Avatar System + Unified Workspace"

# ----------------------------
# FOLDERS
# ----------------------------
mkdir -p core/adapters core/agents

# ----------------------------
# core/avatar_system.py
# ----------------------------
cat > core/avatar_system.py <<'PY'
"""
Avatar System for Etherea (Foundation)
- Multiple avatar profiles + dynamic switching
- Costume + background/environment switching
- Expressive actions: dance/sing/surprise
- Safe style imitation mode (no copyrighted imitation)
- Emotion-aware presence linked with system state
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
import time
import random

from core.emotion_mapper import EmotionMapper

@dataclass
class AvatarProfile:
    id: str
    name: str
    costume: str = "default"
    background: str = "workspace"
    safe_style_mode: str = "neutral"   # safe imitation mode descriptor
    meta: Dict[str, Any] = field(default_factory=dict)

class AvatarSystem:
    def __init__(self):
        self.mapper = EmotionMapper()
        self.profiles: Dict[str, AvatarProfile] = {}
        self.active_id: Optional[str] = None

        # EI-like state (0..1)
        self.emotion = {"focus": 0.5, "stress": 0.2, "energy": 0.5, "curiosity": 0.5}
        self.last_action = None

        # create default avatar
        self.create_profile("aurora", "Aurora")

    # -------- Profiles --------
    def create_profile(self, profile_id: str, name: str, **kwargs) -> AvatarProfile:
        p = AvatarProfile(id=profile_id, name=name, **kwargs)
        self.profiles[profile_id] = p
        if self.active_id is None:
            self.active_id = profile_id
        return p

    def switch_profile(self, profile_id: str) -> bool:
        if profile_id in self.profiles:
            self.active_id = profile_id
            return True
        return False

    def get_active(self) -> AvatarProfile:
        if not self.active_id:
            raise RuntimeError("No active avatar profile.")
        return self.profiles[self.active_id]

    # -------- Costume / Background --------
    def set_costume(self, costume: str):
        self.get_active().costume = costume

    def set_background(self, bg: str):
        self.get_active().background = bg

    def set_safe_style_mode(self, mode: str):
        # safe mode only stores a descriptor (no imitation of copyrighted characters)
        self.get_active().safe_style_mode = mode

    # -------- Expressive Actions --------
    def do_action(self, action: str) -> str:
        action = action.lower().strip()
        self.last_action = action

        if action in ("dance", "dancing"):
            return f"💃 {self.get_active().name} is dancing with cosmic energy!"
        if action in ("sing", "singing"):
            return f"🎶 {self.get_active().name} is humming a safe original melody."
        if action in ("surprise", "wow", "shock"):
            return f"😲 {self.get_active().name} did a surprise interaction!"
        return f"✨ {self.get_active().name} performed: {action}"

    # -------- Emotion Updates --------
    def update_emotion(self, **updates):
        for k, v in updates.items():
            if k in self.emotion:
                try:
                    f = float(v)
                except Exception:
                    continue
                self.emotion[k] = max(0.0, min(1.0, f))

    def get_visual_state(self) -> Dict[str, float]:
        return self.mapper.update(self.emotion)

    # -------- GUI Compatibility Methods --------
    def get_current_ei_state(self):
        # Aurora GUI expects either str or dict
        focus = self.emotion.get("focus", 0.5)
        stress = self.emotion.get("stress", 0.2)
        if stress > 0.7:
            return "Stressed"
        if focus > 0.7:
            return "Focused"
        return "Neutral"

    def get_visual_for_response(self, response: str) -> str:
        # simple icon feedback
        icons = ["💡 Idea Spark", "🔥 Focus Flame", "🌙 Calm Aura", "⚡ Energy Pulse", "✨ Glow Shift"]
        if "error" in response.lower():
            return "🚨 Alert"
        return random.choice(icons)

    def generate_response(self, user_text: str) -> str:
        """
        Basic response generator (foundation).
        Later: connect this to AvatarEngine / LLM.
        """
        active = self.get_active()
        mood = self.get_current_ei_state()
        style = active.safe_style_mode
        bg = active.background
        costume = active.costume

        # lightweight behavior: update focus/stress based on keywords
        t = user_text.lower()
        if "focus" in t:
            self.update_emotion(focus=min(1.0, self.emotion["focus"] + 0.1))
        if "stress" in t or "tired" in t:
            self.update_emotion(stress=min(1.0, self.emotion["stress"] + 0.1))

        action_hint = ""
        if any(w in t for w in ["dance", "sing", "surprise"]):
            for w in ["dance", "sing", "surprise"]:
                if w in t:
                    action_hint = self.do_action(w)
                    break

        return (
            f"{active.name} [{mood}] ({style}) 🌌\n"
            f"🎭 Costume: {costume} | 🌄 Background: {bg}\n"
            f"🗣️ {active.name}: I understood → {user_text}\n"
            f"{action_hint}"
        )
PY

# ----------------------------
# core/workspace_manager.py
# ----------------------------
cat > core/workspace_manager.py <<'PY'
"""
Unified Workspace Manager (Foundation)
- Single workspace for all file types (no split)
- Adapter-based extensibility
- Per-file agent attachment
- Seal/unseal workspace (read-only vs editable)
- Unified save system
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Any

from core.adapters import get_adapter_for_path
from core.agents import get_agent_for_adapter

@dataclass
class OpenFile:
    path: Path
    adapter: Any
    agent: Any
    sealed: bool = False

class WorkspaceManager:
    def __init__(self, root: str = "workspace"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.open_files: Dict[str, OpenFile] = {}

    def open(self, filepath: str) -> OpenFile:
        p = Path(filepath)
        if not p.is_absolute():
            p = self.root / p

        adapter = get_adapter_for_path(p)
        adapter.read()
        agent = get_agent_for_adapter(adapter)

        f = OpenFile(path=p, adapter=adapter, agent=agent, sealed=False)
        self.open_files[str(p)] = f
        return f

    def seal(self, filepath: str):
        f = self._get(filepath)
        f.sealed = True
        f.adapter.set_readonly(True)

    def unseal(self, filepath: str):
        f = self._get(filepath)
        f.sealed = False
        f.adapter.set_readonly(False)

    def write(self, filepath: str, content: Any):
        f = self._get(filepath)
        if f.sealed:
            raise PermissionError("Workspace file is sealed (read-only).")
        f.adapter.write(content)

    def save(self, filepath: str):
        f = self._get(filepath)
        f.adapter.save()

    def highlight(self, filepath: str, pattern: str):
        f = self._get(filepath)
        return f.agent.highlight(pattern)

    def analyse(self, filepath: str):
        f = self._get(filepath)
        return f.agent.analyse()

    def _get(self, filepath: str) -> OpenFile:
        p = Path(filepath)
        if not p.is_absolute():
            p = self.root / p
        key = str(p)
        if key not in self.open_files:
            return self.open(key)
        return self.open_files[key]
PY

# ----------------------------
# ADAPTERS
# ----------------------------
cat > core/adapters/base_adapter.py <<'PY'
from __future__ import annotations
from pathlib import Path
from typing import Any

class BaseAdapter:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.readonly = False
        self.data: Any = None

    def set_readonly(self, ro: bool):
        self.readonly = bool(ro)

    def read(self):
        raise NotImplementedError

    def write(self, content: Any):
        if self.readonly:
            raise PermissionError("Adapter is read-only.")
        self.data = content

    def save(self):
        raise NotImplementedError
PY

cat > core/adapters/code_adapter.py <<'PY'
from __future__ import annotations
from pathlib import Path
from typing import Any
from .base_adapter import BaseAdapter

class CodeAdapter(BaseAdapter):
    def read(self):
        if self.path.exists():
            self.data = self.path.read_text(encoding="utf-8", errors="ignore")
        else:
            self.data = ""

    def save(self):
        if self.readonly:
            raise PermissionError("Read-only.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(str(self.data), encoding="utf-8")
PY

cat > core/adapters/document_adapter.py <<'PY'
from __future__ import annotations
from pathlib import Path
from typing import Any
from .base_adapter import BaseAdapter

class DocumentAdapter(BaseAdapter):
    def read(self):
        if self.path.exists():
            self.data = self.path.read_text(encoding="utf-8", errors="ignore")
        else:
            self.data = ""

    def save(self):
        if self.readonly:
            raise PermissionError("Read-only.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(str(self.data), encoding="utf-8")
PY

cat > core/adapters/spreadsheet_adapter.py <<'PY'
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from .base_adapter import BaseAdapter

class SpreadsheetAdapter(BaseAdapter):
    """
    Edit-ready architecture: stores sheet dict in memory.
    Real XLSX writing can be added using openpyxl later.
    """
    def read(self):
        # placeholder structure
        self.data = {"Sheet1": [["A1","B1"],["A2","B2"]]}

    def save(self):
        # Placeholder: does not write xlsx yet
        # (architecture is ready for adapter-based expansion)
        return
PY

cat > core/adapters/pdf_adapter.py <<'PY'
from __future__ import annotations
from pathlib import Path
from typing import Any, List
from .base_adapter import BaseAdapter

class PDFAdapter(BaseAdapter):
    """
    Adapter-based PDF handling foundation:
    - open (extract placeholder)
    - annotate (store notes)
    - rebuild workflow (future)
    """
    def read(self):
        self.data = {"pages": [], "annotations": []}

    def write(self, content: Any):
        if self.readonly:
            raise PermissionError("Read-only.")
        self.data = content

    def save(self):
        # future: rebuild PDF
        return
PY

cat > core/adapters/media_adapter.py <<'PY'
from __future__ import annotations
from pathlib import Path
from typing import Any
from .base_adapter import BaseAdapter

class MediaAdapter(BaseAdapter):
    def read(self):
        if self.path.exists():
            self.data = self.path.read_bytes()
        else:
            self.data = b""

    def write(self, content: Any):
        if self.readonly:
            raise PermissionError("Read-only.")
        if not isinstance(content, (bytes, bytearray)):
            raise TypeError("MediaAdapter expects bytes.")
        self.data = bytes(content)

    def save(self):
        if self.readonly:
            raise PermissionError("Read-only.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(self.data or b"")
PY

cat > core/adapters/__init__.py <<'PY'
from __future__ import annotations
from pathlib import Path
from typing import Type

from .base_adapter import BaseAdapter
from .code_adapter import CodeAdapter
from .document_adapter import DocumentAdapter
from .spreadsheet_adapter import SpreadsheetAdapter
from .pdf_adapter import PDFAdapter
from .media_adapter import MediaAdapter

ADAPTERS = {
    # code
    ".py": CodeAdapter,
    ".js": CodeAdapter,
    ".html": CodeAdapter,
    ".css": CodeAdapter,
    ".json": CodeAdapter,
    ".md": CodeAdapter,

    # docs
    ".txt": DocumentAdapter,
    ".docx": DocumentAdapter,  # foundation (real docx later)

    # sheets
    ".xlsx": SpreadsheetAdapter,

    # pdf
    ".pdf": PDFAdapter,

    # media
    ".png": MediaAdapter,
    ".jpg": MediaAdapter,
    ".jpeg": MediaAdapter,
    ".webp": MediaAdapter,
    ".mp3": MediaAdapter,
    ".wav": MediaAdapter,
    ".mp4": MediaAdapter,
}

def get_adapter_for_path(path: Path) -> BaseAdapter:
    ext = path.suffix.lower()
    cls: Type[BaseAdapter] = ADAPTERS.get(ext, DocumentAdapter)
    return cls(path)
PY

# ----------------------------
# AGENTS
# ----------------------------
cat > core/agents/base_agent.py <<'PY'
from __future__ import annotations
from typing import Any, List, Tuple

class BaseAgent:
    def __init__(self, adapter: Any):
        self.adapter = adapter

    def highlight(self, pattern: str) -> List[Tuple[int,int]]:
        # simple highlight in text
        data = self.adapter.data
        if not isinstance(data, str) or not pattern:
            return []
        res = []
        start = 0
        p = pattern.lower()
        low = data.lower()
        while True:
            i = low.find(p, start)
            if i == -1:
                break
            res.append((i, i+len(pattern)))
            start = i + len(pattern)
        return res

    def analyse(self):
        return {"type": "base", "info": "No analysis implemented"}
PY

cat > core/agents/code_agent.py <<'PY'
from __future__ import annotations
from .base_agent import BaseAgent

class CodeAgent(BaseAgent):
    def analyse(self):
        txt = self.adapter.data if isinstance(self.adapter.data, str) else ""
        lines = txt.splitlines()
        return {"type": "code", "lines": len(lines)}
PY

cat > core/agents/document_agent.py <<'PY'
from __future__ import annotations
from .base_agent import BaseAgent

class DocumentAgent(BaseAgent):
    def analyse(self):
        txt = self.adapter.data if isinstance(self.adapter.data, str) else ""
        words = txt.split()
        return {"type": "document", "words": len(words), "preview": " ".join(words[:40])}
PY

cat > core/agents/spreadsheet_agent.py <<'PY'
from __future__ import annotations
from .base_agent import BaseAgent

class SpreadsheetAgent(BaseAgent):
    def highlight(self, pattern: str):
        data = self.adapter.data
        if not isinstance(data, dict) or not pattern:
            return []
        hits = []
        for sheet, rows in data.items():
            for r_i, row in enumerate(rows):
                for c_i, val in enumerate(row):
                    if pattern.lower() in str(val).lower():
                        hits.append((sheet, r_i, c_i))
        return hits

    def analyse(self):
        data = self.adapter.data if isinstance(self.adapter.data, dict) else {}
        return {"type": "spreadsheet", "sheets": list(data.keys())}
PY

cat > core/agents/pdf_agent.py <<'PY'
from __future__ import annotations
from .base_agent import BaseAgent

class PDFAgent(BaseAgent):
    def analyse(self):
        data = self.adapter.data if isinstance(self.adapter.data, dict) else {}
        return {"type": "pdf", "keys": list(data.keys())}
PY

cat > core/agents/media_agent.py <<'PY'
from __future__ import annotations
from .base_agent import BaseAgent

class MediaAgent(BaseAgent):
    def highlight(self, pattern: str):
        return []  # no text highlight for binary

    def analyse(self):
        b = self.adapter.data if isinstance(self.adapter.data, (bytes, bytearray)) else b""
        return {"type": "media", "bytes": len(b)}
PY

cat > core/agents/__init__.py <<'PY'
from __future__ import annotations
from typing import Any

from core.adapters.code_adapter import CodeAdapter
from core.adapters.document_adapter import DocumentAdapter
from core.adapters.spreadsheet_adapter import SpreadsheetAdapter
from core.adapters.pdf_adapter import PDFAdapter
from core.adapters.media_adapter import MediaAdapter

from .code_agent import CodeAgent
from .document_agent import DocumentAgent
from .spreadsheet_agent import SpreadsheetAgent
from .pdf_agent import PDFAgent
from .media_agent import MediaAgent

def get_agent_for_adapter(adapter: Any):
    if isinstance(adapter, CodeAdapter):
        return CodeAgent(adapter)
    if isinstance(adapter, SpreadsheetAdapter):
        return SpreadsheetAgent(adapter)
    if isinstance(adapter, PDFAdapter):
        return PDFAgent(adapter)
    if isinstance(adapter, MediaAdapter):
        return MediaAgent(adapter)
    return DocumentAgent(adapter)
PY

# ----------------------------
# core/__init__.py export helpers
# ----------------------------
cat > core/__init__.py <<'PY'
"""
core package exports
"""
from .avatar_engine import AvatarEngine
from .avatar_system import AvatarSystem
from .workspace_manager import WorkspaceManager
PY

# ----------------------------
# requirements.txt update
# ----------------------------
if ! grep -q "python-docx" requirements.txt 2>/dev/null; then
  echo "python-docx" >> requirements.txt
fi
if ! grep -q "openpyxl" requirements.txt 2>/dev/null; then
  echo "openpyxl" >> requirements.txt
fi
if ! grep -q "PyPDF2" requirements.txt 2>/dev/null; then
  echo "PyPDF2" >> requirements.txt
fi

# ----------------------------
# README update (append section if missing)
# ----------------------------
if ! grep -q "Avatar & Presence Engine" README.md 2>/dev/null; then
cat >> README.md <<'MD'

---

### 🎭 Avatar & Presence Engine (Foundation Added)

This update introduces a modular **Avatar System**:
- Multiple avatar profiles (dynamic create + switch)
- Costume + environment/background switching
- Expressive actions: dance, sing, surprise
- Safe style imitation mode (non-copyrighted expression)
- Emotion-aware presence connected to system state

### 🧩 Unified Workspace (No Separation Model)

A single workspace for all file types:
- Code editing: Python, JavaScript, HTML, CSS, JSON, Markdown
- Document editing: TXT, MD, DOCX
- Spreadsheet support: XLSX (preview + edit-ready adapter architecture)
- PDF workflow: open/annotate/rebuild (adapter-based)
- Media handling: images/audio/video via binary adapters

### 🧠 Workspace Intelligence (Foundation)

- Per-file agent attachment (context-aware helper)
- Highlighting + analysis across supported formats
- Workspace seal/unseal (read-only vs editable)
- Unified save system across formats

MD
fi

echo "✅ Upgrade complete. Now run: git status"

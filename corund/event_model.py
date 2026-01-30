from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass(frozen=True)
class Event:
    type: str
    timestamp: str
    source: str
    payload: Dict[str, Any]
    priority: int = 50
    privacy_level: str = "normal"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_event(
    event_type: str,
    source: str,
    payload: Dict[str, Any],
    *,
    priority: int = 50,
    privacy_level: str = "normal",
    timestamp: str | None = None,
) -> Event:
    return Event(
        type=event_type,
        timestamp=timestamp or now_iso(),
        source=source,
        payload=payload,
        priority=priority,
        privacy_level=privacy_level,
    )

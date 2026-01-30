from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from corund.event_bus import event_bus
from corund.os_adapter import OSAdapter
from corund.os_pipeline import OSPipeline, OSOverrides


def main() -> None:
    events = []

    def record(event):
        events.append(event)

    event_bus.subscribe(record)

    pipeline = OSPipeline(OSAdapter(dry_run=True))
    overrides = OSOverrides()

    print("== open folder ==")
    print(pipeline.handle_intent("OPEN_FOLDER", {"path": "workspace", "confirm": True}, overrides=overrides))

    print("\n== open url blocked by dnd ==")
    overrides.dnd = True
    print(pipeline.handle_intent("OPEN_URL", {"url": "https://example.com", "confirm": True}, overrides=overrides))

    print("\n== reveal path ==")
    overrides.dnd = False
    print(pipeline.handle_intent("REVEAL_PATH", {"path": "README.md", "confirm": True}, overrides=overrides))

    print("\n== Events ==")
    for event in events:
        print(f"{event.type} {event.payload}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from corund.aurora_actions import ActionRegistry
from corund.aurora_pipeline import AuroraDecisionPipeline
from corund.aurora_state import AuroraStateStore
from corund.workspace_manager import WorkspaceManager
from corund.workspace_registry import WorkspaceRegistry


def main() -> None:
    registry = ActionRegistry.default()
    workspace_manager = WorkspaceManager()
    workspace_registry = WorkspaceRegistry()
    state_store = AuroraStateStore(registry)
    pipeline = AuroraDecisionPipeline(
        registry=registry,
        workspace_registry=workspace_registry,
        workspace_manager=workspace_manager,
        state_store=state_store,
    )

    events = []

    def record(event):
        events.append(event)

    pipeline.subscribe(record)

    def show(label: str) -> None:
        print(f"\n== {label} ==")
        print(state_store.get_canvas_state())

    show("initial")

    pipeline.handle_intent("set_mode_idle")
    show("mode idle")

    pipeline.handle_intent("set_mode_focus")
    show("mode focus")

    pipeline.handle_intent("set_mode_break")
    show("mode break")

    pipeline.handle_intent("workspace_create")
    pipeline.handle_intent("workspace_save_snapshot")
    show("workspace saved")

    pipeline.handle_intent("toggle_dnd_on")
    pipeline.handle_intent("workspace_save_snapshot")
    show("dnd blocked")

    summary = Counter(event.type for event in events)
    summary = Counter(event.event_type for event in events)
    print("\n== Events summary ==")
    for event_type, count in summary.items():
        print(f"{event_type}: {count}")


if __name__ == "__main__":
    main()

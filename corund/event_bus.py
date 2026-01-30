from __future__ import annotations

from typing import Callable, List

from corund.event_model import Event


class EventBus:
    def __init__(self) -> None:
        self._listeners: List[Callable[[Event], None]] = []

    def subscribe(self, listener: Callable[[Event], None]) -> None:
        self._listeners.append(listener)

    def emit(self, event: Event) -> None:
        for listener in self._listeners:
            listener(event)


event_bus = EventBus()

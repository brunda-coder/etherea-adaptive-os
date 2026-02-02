from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine, DefaultDict, List

from corund.event_model import Event

# Define a listener type that can be a regular function or a coroutine
Listener = Callable[[Event], Coroutine[Any, Any, None] | None]

class EventBus:
    """
    A robust EventBus that allows subscription to specific event types
    and supports both synchronous and asynchronous listeners.
    """

    def __init__(self) -> None:
        """Initializes the EventBus."""
        self._listeners: DefaultDict[str, List[Listener]] = defaultdict(list)
        self._wildcard_listeners: List[Listener] = []

    def subscribe(self, listener: Listener, event_type: str | None = None) -> Callable[[], None]:
        """
        Subscribe a listener to a specific event type or all events.

        Args:
            listener: The function to call when the event is emitted.
            event_type: The type of event to listen for. If None, the listener
                        will receive all events.

        Returns:
            A function that can be called to unsubscribe the listener.
        """
        if event_type:
            self._listeners[event_type].append(listener)
        else:
            self._wildcard_listeners.append(listener)

        def unsubscribe() -> None:
            """Removes the listener from the bus."""
            self.unsubscribe(listener, event_type)

        return unsubscribe

    def unsubscribe(self, listener: Listener, event_type: str | None = None) -> None:
        """
        Unsubscribe a listener from an event type or all events.

        Args:
            listener: The listener function to remove.
            event_type: The event type from which to unsubscribe. If None,
                        unsubscribes from the wildcard listeners.
        """
        try:
            if event_type:
                if listener in self._listeners[event_type]:
                    self._listeners[event_type].remove(listener)
            else:
                if listener in self._wildcard_listeners:
                    self._wildcard_listeners.remove(listener)
        except ValueError:
            # Listener not found, which can happen and is not an error.
            pass

    async def emit(self, event: Event) -> None:
        """
        Emit an event, calling all subscribed listeners for the event's type
        and all wildcard listeners. Runs async listeners concurrently.
        """
        listeners_to_call = self._listeners[event.type] + self._wildcard_listeners

        if not listeners_to_call:
            return

        # Separate sync and async listeners
        async_tasks = []

        for listener in listeners_to_call:
            result = listener(event)
            if asyncio.iscoroutine(result):
                async_tasks.append(result)

        # Await all async tasks concurrently
        if async_tasks:
            await asyncio.gather(*async_tasks)

# Global singleton instance of the EventBus.
event_bus = EventBus()

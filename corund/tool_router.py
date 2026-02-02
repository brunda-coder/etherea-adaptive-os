import asyncio
from typing import Callable, Dict, Any, Coroutine

from corund.event_bus import event_bus
from corund.event_model import Event

# A tool is a function that can be sync or async and takes arguments
Tool = Callable[..., Coroutine[Any, Any, None] | None]

class ToolRouter:
    """
    Executes actions chosen by the PolicyEngine or other agents.
    It maps a tool name to an executable function.
    """

    def __init__(self):
        self._tool_registry: Dict[str, Tool] = {}
        print("ToolRouter initialized.")
        # Subscribe to decision events from agents/policy engine
        event_bus.subscribe(self._handle_decision, event_type="agent.decision")

    def register_tool(self, name: str, func: Tool):
        """
        Register a tool that the router can execute.

        Args:
            name: The name to identify the tool (e.g., "ui.set_density").
            func: The function to execute.
        """
        if name in self._tool_registry:
            print(f"⚠️ Tool '{name}' is being overwritten.")
        self._tool_registry[name] = func
        print(f"Tool '{name}' registered.")

    async def _handle_decision(self, event: Event):
        """
        Handles 'agent.decision' events from the event bus.
        """
        if event.type != "agent.decision":
            return

        tool_name = event.payload.get("tool_name")
        args = event.payload.get("args", {})

        if not tool_name:
            print(f"ERROR: 'agent.decision' event received without a 'tool_name'. Payload: {event.payload}")
            return

        tool_func = self._tool_registry.get(tool_name)

        if not tool_func:
            print(f"ERROR: Tool '{tool_name}' not found in registry.")
            return

        print(f"ROUTING: Executing tool '{tool_name}' with args: {args}")
        try:
            # Execute the tool
            result = tool_func(**args)
            if asyncio.iscoroutine(result):
                await result
            print(f"ROUTING: Tool '{tool_name}' executed successfully.")
        except Exception as e:
            print(f"ERROR: Exception while executing tool '{tool_name}': {e}")

# Singleton instance
tool_router = ToolRouter()
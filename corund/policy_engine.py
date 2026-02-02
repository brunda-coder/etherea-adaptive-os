import asyncio
from corund.state import get_state
from corund.event_bus import event_bus
from corund.event_model import create_event
# Import the behavior definitions
from corund.workspace_behaviors import WORKSPACE_BEHAVIORS

class PolicyEngine:
    """
    The Policy/Decision Engine for Etherea. This is the adaptive OS brain.
    It runs a continuous loop to evaluate the global state and make decisions.
    """
    def __init__(self):
        self.state = get_state()
        self._running = False
        self._task = None

    async def _emit_decision(self, tool_name: str, args: dict, reason: str):
        """
        Logs the decision and emits it to the event bus for the ToolRouter.
        """
        print(f"DECISION: {reason}. Action: {tool_name} with {args}")
        event = create_event(
            event_type="agent.decision",
            source="PolicyEngine",
            payload={
                "tool_name": tool_name,
                "args": args,
                "reason": reason
            }
        )
        await event_bus.emit(event)

    async def _evaluate_state(self):
        """
        The core logic of the Policy Engine. This method is called repeatedly
        to evaluate the current state and decide on actions based on the active
        workspace's behavior.
        """
        # Get the behavior for the current workspace
        workspace_name = self.state.current_workspace
        behavior = WORKSPACE_BEHAVIORS.get(workspace_name)

        if not behavior:
            print(f"WARNING: No behavior defined for workspace: {workspace_name}")
            return

        # --- Agent Autonomy Rules ---
        # If autonomy is 'silent', the agent should not perform any proactive actions.
        if behavior["agent_autonomy"] == "silent":
            return # Stop further evaluation for this cycle

        # --- Proactive Suggestion Rules ---
        # These actions are only considered if the workspace allows for proactive suggestions.
        if behavior["allow_proactive_suggestions"]:
            # Rule: If cognitive load is high, suggest a break.
            # This is a critical notification, so it respects the notification level.
            if self.state.cognitive_load > 0.9 and behavior["notification_level"] in ["critical", "all"]:
                await self._emit_decision(
                    tool_name="notifications.show",
                    args={"message": "Cognitive load is high. Consider taking a short break."},
                    reason=f"High cognitive load detected in {workspace_name} workspace"
                )
            
            # Example of a workspace-specific proactive action for the 'Build' workspace
            if workspace_name == "Build" and self.state.activity_state == "idle":
                # This is a placeholder for a more complex rule, e.g., checking for unsaved files
                # or suggesting to run tests after a period of inactivity.
                pass # Add more specific build-related rules here

    async def _run(self):
        """
        The main loop for the policy engine.
        """
        while self._running:
            await self._evaluate_state()
            # The evaluation frequency can be adjusted based on the system's state.
            await asyncio.sleep(5) # Evaluate every 5 seconds for now

    def start(self):
        """
        Starts the Policy Engine's decision loop in the background.
        """
        if not self._running:
            print("Starting Policy Engine...")
            self._running = True
            self._task = asyncio.create_task(self._run())

    def stop(self):
        """
        Stops the Policy Engine's decision loop.
        """
        if self._running:
            print("Stopping Policy Engine...")
            self._running = False
            if self._task:
                self._task.cancel()
                self._task = None

# Singleton instance of the PolicyEngine
policy_engine = PolicyEngine()

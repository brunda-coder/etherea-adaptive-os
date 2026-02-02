from corund.tool_router import tool_router

def set_ui_density(density: str):
    """Placeholder tool to change UI density."""
    print(f"SYSTEM TOOL: Setting UI density to {density}")

def show_notification(message: str):
    """Placeholder tool to show a notification."""
    print(f"SYSTEM TOOL: Showing notification: '{message}'")


def register_system_tools():
    """Registers all system tools with the ToolRouter."""
    print("Registering system tools...")
    tool_router.register_tool("ui.set_density", set_ui_density)
    tool_router.register_tool("notifications.show", show_notification)
    print("System tools registered.")

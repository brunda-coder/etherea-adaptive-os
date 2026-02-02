from typing import TypedDict, Literal, Dict

# Type definitions for clarity
AgentAutonomy = Literal['silent', 'reactive', 'proactive']
UIDensity = Literal['minimal', 'standard', 'dense']
NotificationLevel = Literal['none', 'critical', 'all']

class WorkspaceBehavior(TypedDict):
    """Defines the operational parameters for a workspace."""
    agent_autonomy: AgentAutonomy
    ui_density: UIDensity
    notification_level: NotificationLevel
    allow_proactive_suggestions: bool
    description: str

# As per the blueprint, we define the specific behavior for each of the five core workspaces.
# This dictionary will be the single source of truth for how a workspace should behave.
WORKSPACE_BEHAVIORS: Dict[str, WorkspaceBehavior] = {
    "Study": {
        "agent_autonomy": "reactive",
        "ui_density": "standard",
        "notification_level": "critical",
        "allow_proactive_suggestions": True,
        "description": "Focus on learning. Agent assists when asked, UI is clean."
    },
    "Build": {
        "agent_autonomy": "proactive",
        "ui_density": "dense",
        "notification_level": "all",
        "allow_proactive_suggestions": True,
        "description": "Coding environment. Agent is highly proactive, UI shows more info."
    },
    "Research": {
        "agent_autonomy": "proactive",
        "ui_density": "standard",
        "notification_level": "all",
        "allow_proactive_suggestions": True,
        "description": "Information gathering. Agent helps with summarization and discovery."
    },
    "Calm": {
        "agent_autonomy": "silent",
        "ui_density": "minimal",
        "notification_level": "none",
        "allow_proactive_suggestions": False,
        "description": "Relaxation space. Minimal distractions."
    },
    "Deep Work": {
        "agent_autonomy": "silent",
        "ui_density": "minimal",
        "notification_level": "none",
        "allow_proactive_suggestions": False,
        "description": "Intense focus. No interruptions from the agent or UI."
    }
}

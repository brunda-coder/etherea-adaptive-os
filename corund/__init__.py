"""
core package exports (safe imports)
"""

# Optional: AvatarEngine is loaded defensively so app startup remains resilient.
try:
    from .avatar_engine import AvatarEngine  # noqa: F401
except Exception:
    AvatarEngine = None  # type: ignore

from .avatar_system import AvatarSystem  # noqa: F401
from .workspace_manager import WorkspaceManager  # noqa: F401

"""Compatibility shim.

This repo renamed the main package from `core` -> `corund`.

Goals:
- Keep old imports working (`import core`, `import core.voice_engine`, etc.).
- Avoid recursion/alias weirdness.
- Keep startup light and predictable.

Implementation:
- Import `corund` once.
- Point `core.__path__` at `corund` so `core.<submodule>` resolves to files inside `corund/`.
- Forward attribute access to the `corund` package.
"""

from __future__ import annotations

import importlib
from typing import Any

_corund = importlib.import_module("corund")

# Let `import core.some_module` find modules inside the corund package directory.
__path__ = getattr(_corund, "__path__", [])  # type: ignore

def __getattr__(name: str) -> Any:
    return getattr(_corund, name)

def __dir__() -> list[str]:
    return sorted(set(dir(_corund)))

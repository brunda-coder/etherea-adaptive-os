#!/usr/bin/env python3
from __future__ import annotations

import compileall
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def report(status: str, name: str, detail: str) -> bool:
    print(f"[{status}] {name}: {detail}")
    return status == "PASS"


def main() -> int:
    failures = 0

    # 1) Key imports.
    for mod in [
        "corund.capabilities",
        "corund.workspace_ai.router",
        "corund.workspace_ai.workspace_controller",
        "corund.ui.avatar.avatar_brain",
        "corund.resource_manager",
    ]:
        try:
            importlib.import_module(mod)
            report("PASS", "import", mod)
        except Exception as exc:
            failures += 1
            report("FAIL", "import", f"{mod} -> {exc}")

    # 2) Compileall sanity.
    compiled = compileall.compile_dir(str(ROOT / "corund"), quiet=1, maxlevels=10)
    if not report("PASS" if compiled else "FAIL", "compileall", "python -m compileall corund"):
        failures += 1

    # 3) Capability detection.
    try:
        from corund.capabilities import detect_capabilities

        caps = detect_capabilities().to_dict()
        report("PASS", "capabilities", str(caps))
    except Exception as exc:
        failures += 1
        report("FAIL", "capabilities", str(exc))

    # 4) Command parser/router samples.
    try:
        from corund.workspace_ai.router import WorkspaceAIRouter
        from corund.workspace_ai.workspace_controller import WorkspaceController
        from corund.workspace_manager import WorkspaceManager

        router = WorkspaceAIRouter()
        controller = WorkspaceController(WorkspaceManager())

        samples = [
            "open aurora",
            "set focus mode for 25 minutes",
            "summarize my session",
        ]
        for text in samples:
            route = router.route(text)
            handled = controller.handle_command(text, source="runtime_selftest")
            if route.get("action") == "unknown":
                failures += 1
                report("FAIL", "command", f"{text!r} -> unknown route={route} handled={handled}")
            else:
                report("PASS", "command", f"{text!r} -> route={route.get('action')} handled={handled.get('action')}")
    except Exception as exc:
        failures += 1
        report("FAIL", "command_pipeline", f"missing symbol or runtime error: {exc}")

    # 5) Avatar controller update tick.
    try:
        from PySide6.QtCore import QRectF
        from corund.ui.avatar.avatar_brain import AvatarBrain

        brain = AvatarBrain()
        target = brain.update(QRectF(0, 0, 400, 260), now=1.0)
        report("PASS", "avatar_update", f"update(dt) equivalent via now tick target={target}")
    except Exception as exc:
        failures += 1
        report("FAIL", "avatar_update", f"missing symbol or runtime error: {exc}")

    # 6) Missing asset should safely return None.
    try:
        from corund.resource_manager import ResourceManager

        resolved = ResourceManager.resolve_asset("missing/not_real.asset")
        if resolved is None:
            report("PASS", "asset_resolver", "resolve_asset returned None safely")
        else:
            failures += 1
            report("FAIL", "asset_resolver", f"expected None, got {resolved}")
    except Exception as exc:
        failures += 1
        report("FAIL", "asset_resolver", str(exc))

    print(f"SUMMARY failures={failures}")
    return 2 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import json
import logging
import os
import platform
import sys
import traceback
from dataclasses import dataclass, field
from logging.handlers import RotatingFileHandler
from pathlib import Path

from corund.app_runtime import is_frozen, user_data_dir
from corund.resource_manager import ResourceManager


@dataclass
class DiagnosticReport:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, object] = field(default_factory=dict)


class RuntimeDiagnostics:
    def __init__(self, *, debug: bool = False) -> None:
        self.debug = debug
        self.logger = logging.getLogger("etherea.runtime")
        self._configure_logging()

    def _configure_logging(self) -> None:
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        self.logger.handlers.clear()

        logs_dir = ResourceManager.logs_dir()
        log_path = logs_dir / "etherea.log"
        handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        console = logging.StreamHandler(stream=sys.stdout)
        console.setFormatter(formatter)
        self.logger.addHandler(console)

    def log_exception(self, exc_type, exc, tb) -> None:
        self.logger.error("Uncaught exception", exc_info=(exc_type, exc, tb))

    def run_startup_checks(self) -> DiagnosticReport:
        errors: list[str] = []
        warnings: list[str] = []
        rm = ResourceManager()

        manifest_path = Path(rm.resolve("corund/assets/etherea_assets_manifest.json"))
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                for asset in manifest.get("audio", []) + manifest.get("animations", []) + manifest.get("models", []):
                    if not rm.exists(asset):
                        errors.append(f"Missing asset: {asset}")
            except json.JSONDecodeError as exc:
                warnings.append(f"Asset manifest unreadable: {exc}")
        else:
            warnings.append("Asset manifest not found.")

        required_assets = [
            "assets/audio/ui_click.wav",
            "assets/audio/ui_success.wav",
            "assets/audio/ui_whoosh.wav",
            "assets/avatar/face_idle.webp",
            "assets/demo/demo_script_01.json",
        ]
        for asset in required_assets:
            if not rm.exists(asset):
                errors.append(f"Missing asset: {asset}")

        data_dir = user_data_dir()
        if not data_dir.exists():
            errors.append(f"User data directory missing: {data_dir}")
        else:
            try:
                test_path = data_dir / ".write_test"
                test_path.write_text("ok", encoding="utf-8")
                test_path.unlink()
            except OSError as exc:
                errors.append(f"User data directory not writable: {exc}")

        if is_frozen():
            plugin_path = Path(getattr(sys, "_MEIPASS", "")) / "PySide6" / "plugins" / "platforms"
            if not plugin_path.exists():
                errors.append("Missing Qt platform plugins (platforms folder).")

        details = self._build_details()
        self._log_report(errors, warnings, details)
        return DiagnosticReport(ok=not errors, errors=errors, warnings=warnings, details=details)

    def _log_report(self, errors: list[str], warnings: list[str], details: dict[str, object]) -> None:
        if errors:
            for err in errors:
                self.logger.error(err)
        if warnings:
            for warn in warnings:
                self.logger.warning(warn)
        self.logger.info("Diagnostics: %s", json.dumps(details, ensure_ascii=False))

    def _build_details(self) -> dict[str, object]:
        return {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "executable": sys.executable,
            "argv": sys.argv,
            "frozen": is_frozen(),
            "base_path": getattr(sys, "_MEIPASS", ""),
            "data_dir": str(user_data_dir()),
        }

    def diagnostics_text(self, report: DiagnosticReport | None = None) -> str:
        payload = report.details if report else self._build_details()
        return json.dumps(payload, indent=2, ensure_ascii=False)

    def self_check_marker(self) -> Path:
        return user_data_dir() / "self_check_ok.txt"

    def should_run_self_check(self) -> bool:
        return not self.self_check_marker().exists()

    def mark_self_check_ok(self) -> None:
        self.self_check_marker().write_text("ok", encoding="utf-8")

    def run_ui_self_check(self, controller) -> DiagnosticReport:
        errors: list[str] = []
        warnings: list[str] = []

        window = controller.window
        if not window.aurora_bar.isVisible():
            errors.append("Aurora ring is not visible.")
        if not window.avatar_panel.isVisible():
            errors.append("Avatar panel is not visible.")
        if not getattr(window.ethera_dock, "command_palette", None):
            errors.append("Command palette missing.")
        else:
            input_field = window.ethera_dock.command_palette.input
            if input_field is None:
                errors.append("Command palette input missing.")

        workspaces = controller.get_available_workspaces()
        if len(workspaces) > 1:
            current = controller.workspace_registry.get_current()
            target = next(ws for ws in workspaces if ws.name != current.name)
            try:
                controller.switch_workspace(target.name)
                controller.switch_workspace(current.name)
            except Exception as exc:
                errors.append(f"Workspace switch failed: {exc}")
        else:
            warnings.append("Only one workspace available; switch check skipped.")

        details = self._build_details()
        return DiagnosticReport(ok=not errors, errors=errors, warnings=warnings, details=details)

    def write_self_test_marker(self) -> None:
        marker = user_data_dir() / "self_test_ok.txt"
        marker.write_text("ok", encoding="utf-8")

    def write_self_test_failure(self, errors: list[str]) -> None:
        marker = user_data_dir() / "self_test_fail.txt"
        marker.write_text("\n".join(errors), encoding="utf-8")

    def format_exception(self, exc: Exception) -> str:
        return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

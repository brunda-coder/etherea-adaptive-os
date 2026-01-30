from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class OSResult:
    ok: bool
    message: str
    detail: Optional[str] = None


class OSAdapter:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run

    def open_file(self, path: str) -> OSResult:
        return self._open_path(path, mode="file")

    def open_folder(self, path: str) -> OSResult:
        return self._open_path(path, mode="folder")

    def reveal_in_explorer(self, path: str) -> OSResult:
        return self._reveal_path(path)

    def open_url(self, url: str) -> OSResult:
        if self.dry_run:
            return OSResult(ok=True, message=f"DRY_RUN open_url: {url}")
        try:
            if sys.platform.startswith("win"):
                os.startfile(url)  # type: ignore[attr-defined]
            elif sys.platform.startswith("darwin"):
                subprocess.check_call(["open", url])
            else:
                subprocess.check_call(["xdg-open", url])
            return OSResult(ok=True, message=f"Opened URL: {url}")
        except Exception as exc:
            return OSResult(ok=False, message="open_url failed", detail=str(exc))

    def launch_app(self, path: str, args: Optional[List[str]] = None) -> OSResult:
        args = args or []
        if self.dry_run:
            return OSResult(ok=True, message=f"DRY_RUN launch_app: {path} {' '.join(args)}")
        try:
            if sys.platform.startswith("win"):
                if args:
                    subprocess.Popen([path] + args)
                else:
                    os.startfile(path)  # type: ignore[attr-defined]
                os.startfile(path)  # type: ignore[attr-defined]
            else:
                subprocess.Popen([path] + args)
            return OSResult(ok=True, message=f"Launched app: {path}")
        except Exception as exc:
            return OSResult(ok=False, message="launch_app failed", detail=str(exc))

    def _open_path(self, path: str, mode: str) -> OSResult:
        resolved = str(Path(path).expanduser().resolve())
        if self.dry_run:
            return OSResult(ok=True, message=f"DRY_RUN open_{mode}: {resolved}")
        try:
            if sys.platform.startswith("win"):
                os.startfile(resolved)  # type: ignore[attr-defined]
            elif sys.platform.startswith("darwin"):
                subprocess.check_call(["open", resolved])
            else:
                subprocess.check_call(["xdg-open", resolved])
            return OSResult(ok=True, message=f"Opened {mode}: {resolved}")
        except Exception as exc:
            return OSResult(ok=False, message=f"open_{mode} failed", detail=str(exc))

    def _reveal_path(self, path: str) -> OSResult:
        resolved = str(Path(path).expanduser().resolve())
        if self.dry_run:
            return OSResult(ok=True, message=f"DRY_RUN reveal_in_explorer: {resolved}")
        try:
            if sys.platform.startswith("win"):
                subprocess.check_call(["explorer", "/select,", resolved])
            elif sys.platform.startswith("darwin"):
                subprocess.check_call(["open", "-R", resolved])
            else:
                subprocess.check_call(["xdg-open", str(Path(resolved).parent)])
            return OSResult(ok=True, message=f"Revealed path: {resolved}")
        except Exception as exc:
            return OSResult(ok=False, message="reveal_in_explorer failed", detail=str(exc))

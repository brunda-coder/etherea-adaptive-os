import os
import subprocess
import threading
import json
import time
from typing import List, Dict, Optional
try:
    from PySide6.QtCore import QObject, Signal
except Exception:
    class QObject:  # minimal stub
        pass
    def Signal(*a, **k):
        return None

class ToolRouter(QObject):
    """
    UPGRADED SPINE (v1.0 Contract)
    Safety-first, Agent-ready tool interface.
    """
    command_completed = Signal(dict)
    file_updated = Signal(str)

    # Safety Policy
    COMMAND_ALLOWLIST = ["python", "pip", "pytest", "dir", "ls", "mkdir", "echo", "git", "type", "cat"]
    COMMAND_DENYLIST = ["rm -rf /", "format", "del /s", "shred", "mkfs"]

    _instance = None

    def __init__(self):
        super().__init__()
        self.root_dir = os.getcwd()
        self.log_path = os.path.join(self.root_dir, "logs", "tool_calls.jsonl")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = ToolRouter()
        return cls._instance

    def _log_call(self, tool_name: str, args: dict, result: dict):
        """Append tool execution to the audit log."""
        log_entry = {
            "timestamp": time.time(),
            "tool": tool_name,
            "args": args,
            "result": {
                "success": result.get("success", False),
                "exit_code": result.get("exit_code"),
                "error": result.get("error")
            }
        }
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except: pass

    def _is_safe_path(self, path: str) -> bool:
        """Enforce CWD sandbox."""
        full_path = os.path.abspath(os.path.join(self.root_dir, path))
        return full_path.startswith(self.root_dir)

    def list_dir(self, rel_path: str = ".", depth: int = 2) -> dict:
        """LIST(dir, depth): Recursive listing with safety check."""
        if not self._is_safe_path(rel_path):
            return {"success": False, "error": "Access Denied: Path outside sandbox."}
        
        try:
            results = []
            full_path = os.path.join(self.root_dir, rel_path)
            for root, dirs, files in os.walk(full_path):
                curr_rel = os.path.relpath(root, self.root_dir)
                if curr_rel.count(os.sep) >= depth:
                    continue
                for f in files:
                    results.append(os.path.join(curr_rel, f))
            
            res = {"success": True, "files": results}
            self._log_call("LIST", {"path": rel_path}, res)
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_file(self, rel_path: str) -> dict:
        """READ(path): Robust reading within sandbox."""
        if not self._is_safe_path(rel_path):
            return {"success": False, "error": "Access Denied."}
        
        try:
            full_path = os.path.join(self.root_dir, rel_path)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            res = {"success": True, "content": content}
            self._log_call("READ", {"path": rel_path}, res)
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, rel_path: str, content: str, mode: str = "replace") -> dict:
        """WRITE(path, content, mode): Replaces or patches file."""
        if not self._is_safe_path(rel_path):
            return {"success": False, "error": "Access Denied."}
        
        try:
            full_path = os.path.join(self.root_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            if mode == "patch":
                # Multi-line append/replace (Mock for now, real agents use diff/match)
                with open(full_path, "a", encoding="utf-8") as f:
                    f.write("\n" + content)
            else:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
            
            res = {"success": True, "path": rel_path}
            self._log_call("WRITE", {"path": rel_path, "mode": mode}, res)
            self.file_updated.emit(rel_path)
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_command(self, cmd_string: str):
        """RUN(cmd): Secure shell execution with allowlist."""
        # Safety Check
        base_cmd = cmd_string.split(" ")[0].lower()
        if base_cmd not in self.COMMAND_ALLOWLIST:
            self.command_completed.emit({"success": False, "error": f"Command '{base_cmd}' is NOT in allowlist."})
            return

        for forbidden in self.COMMAND_DENYLIST:
            if forbidden in cmd_string.lower():
                self.command_completed.emit({"success": False, "error": f"Security Risk: Forbidden pattern detected."})
                return

        thread = threading.Thread(target=self._exec_cmd, args=(cmd_string,), daemon=True)
        thread.start()

    def _exec_cmd(self, cmd: str):
        try:
            process = subprocess.Popen(
                cmd, shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                cwd=self.root_dir
            )
            stdout, stderr = process.communicate(timeout=30)
            
            res = {
                "command": cmd,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": process.returncode,
                "success": process.returncode == 0
            }
            self._log_call("RUN", {"cmd": cmd}, res)
            self.command_completed.emit(res)
        except Exception as e:
            self.command_completed.emit({"success": False, "error": str(e)})

    def search_files(self, pattern: str, rel_path: str = ".") -> dict:
        """SEARCH(text, path): Grep-like search within sandbox."""
        if not self._is_safe_path(rel_path):
            return {"success": False, "error": "Access Denied."}
        
        try:
            matches = []
            full_path = os.path.join(self.root_dir, rel_path)
            for root, _, files in os.walk(full_path):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as file:
                            for i, line in enumerate(file, 1):
                                if pattern in line:
                                    matches.append({
                                        "file": os.path.relpath(fp, self.root_dir),
                                        "line": i,
                                        "content": line.strip()
                                    })
                    except: continue
            
            res = {"success": True, "matches": matches[:50]} # Cap at 50
            self._log_call("SEARCH", {"pattern": pattern}, res)
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

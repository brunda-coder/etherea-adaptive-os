import logging
import threading
import time
from typing import List, Dict, Optional, Callable

from corund.tools.router import ToolRouter
from corund.tools.verifier import Verifier
try:
    from PySide6.QtCore import QObject, Signal
except Exception:
    class QObject:  # minimal stub
        pass
    def Signal(*a, **k):
        return None


class IntelligentAgent(QObject):
    """
    THE BRAIN (v1.0)
    Orchestrates the Agent Loop: Plan -> Execute -> Observe -> Verify.
    """
    status_updated = Signal(str)
    thought_emitted = Signal(str)
    tool_invocation_emitted = Signal(dict) # tool, args
    tool_result_emitted = Signal(dict)     # tool, success, stdout, stderr, exit_code
    plan_step_started = Signal(int, str)
    task_completed = Signal(bool, str)
    task_result_card_emitted = Signal(dict) # Final card data

    def __init__(self):
        super().__init__()
        self.router = ToolRouter.instance()
        self.verifier = Verifier()
        self._current_plan: List[str] = []

        # Bridge Router signals to Agent signals for NEXT 6
        self.router.command_completed.connect(self._on_tool_finished)

    def _on_tool_finished(self, result: dict):
        # Result contains: command, stdout, stderr, exit_code, success
        self.tool_result_emitted.emit({
            "tool": "RUN",
            **result
        })

    def execute_task(self, goal: str):
        """
        Main Agent Loop.
        1. Understand -> Goal
        2. Plan -> Steps
        3. Loop -> Execute & Observe
        4. Verify -> Finish
        """
        # STEP 1: Plan (Simulated/Canned for now, will connect to LLM later)
        self.status_updated.emit(f"Planning for: {goal}")

        # Simple heuristics for 'Fix my build' or 'Update README'
        if "readme" in goal.lower():
            self._current_plan = [
                "READ('README.md')",
                "WRITE('README.md', new_content)",
                "VERIFY"
            ]
        elif "fix" in goal.lower():
            self._current_plan = [
                "RUN('pytest')",
                "SEARCH('Error')",
                "READ('relevant_file.py')",
                "WRITE('relevant_file.py', patch)",
                "VERIFY"
            ]
        else:
            self._current_plan = ["RUN('dir')", "VERIFY"]

        self._run_loop()

    def _run_loop(self):
        success = True
        summary = "Task completed successfully."
        evidence_list = []

        for i, step in enumerate(self._current_plan):
            self.plan_step_started.emit(i, step)
            self.status_updated.emit(f"Step {i+1}: {step}")
            self.thought_emitted.emit(f"Executing: {step}")

            tool_res = {"success": True}  # Default

            if "READ" in step:
                self.tool_invocation_emitted.emit({"tool": "READ", "path": "main.py"})
                tool_res = self.router.read_file("main.py")
                self.tool_result_emitted.emit({"tool": "READ", **tool_res})
                evidence_list.append(f"Read main.py ({len(tool_res.get('content', ''))} bytes)")
            elif "WRITE" in step:
                self.tool_invocation_emitted.emit({"tool": "WRITE", "path": "main.py", "mode": "patch"})
                tool_res = self.router.write_file("main.py", "# Agent Updated", mode="patch")
                self.tool_result_emitted.emit({"tool": "WRITE", **tool_res})
                evidence_list.append("Patched main.py")
            elif "RUN" in step:
                self.tool_invocation_emitted.emit({"tool": "RUN", "cmd": "dir"})
                # RUN is async in ToolRouter, the result comes via signal
                # For this sequence runner, we'll simulate observation
                self.router.run_command("dir")
                evidence_list.append("Executed system command 'dir'")
            elif "VERIFY" in step:
                self.thought_emitted.emit("Running safety verification...")
                v_res = self.verifier.verify_syntax(".")
                if not v_res["success"]:
                    success = False
                    summary = f"Verification failed: {v_res.get('error')}"
                    self.thought_emitted.emit(f"ERROR: {summary}")
                    break
                self.thought_emitted.emit("Verification passed.")
                evidence_list.append("Syntax verification passed")

        # Emit Final Result Card (Strict Visibility)
        card = {
            "title": "Agentic Task",
            "status": "SUCCESS" if success else "FAILED",
            "evidence": evidence_list,
            "location": "Terminal Panel & Logs",
            "summary": summary
        }
        self.task_result_card_emitted.emit(card)
        self.task_completed.emit(success, summary)

# ==========================
# FocusGuardian (Supervisor)
# ==========================
import threading
import time
from typing import Optional, Callable


class FocusGuardian:
    """
    Not a new agent brain — a supervisor around existing systems.

    Purpose:
      - Keep distraction control during focus sessions (exam/deep_work).
      - Provide gentle nudges (optional voice) with throttling.
      - Never executes tools automatically (safe & professor-friendly).
    """

    def __init__(
        self,
        workspace_controller,
        *,
        voice_engine=None,
        log_cb: Optional[Callable[[str], None]] = None,
    ):
        self.ws = workspace_controller
        self.voice = voice_engine
        self.log = log_cb or (lambda m: None)

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_nudge_ts = 0.0

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.log("🛡️ FocusGuardian started")

    def stop(self) -> None:
        self._running = False
        self.log("🛑 FocusGuardian stopped")

    def _loop(self) -> None:
        while self._running:
            try:
                self.tick()
            except Exception:
                pass
            time.sleep(1.0)

    def tick(self) -> None:
        """
        Once per second background tick.
        """
        try:
            mode = getattr(self.ws, "active_mode", "study")
        except Exception:
            mode = "study"

        try:
            secs_left = int(self.ws.focus_seconds_left())
        except Exception:
            secs_left = 0

        if secs_left <= 0:
            return

        # Only nudge in strict modes.
        if mode not in ("deep_work", "exam"):
            return

        now = time.time()
        # Throttle: max once per 3 minutes
        if now - self._last_nudge_ts < 180:
            return
        self._last_nudge_ts = now

        mm = max(0, secs_left // 60)
        msg = f"Stay with it. {mm} minutes left. One clean push. 🧠✨"
        self.log(f"🛡️ FocusGuardian nudge: {msg}")

        if self.voice is not None:
            try:
                self.voice.speak(msg, language="en-IN")
            except Exception:
                pass


class EthereaAgent(IntelligentAgent):
    """Compatibility wrapper expected by audits and registry dry-runs."""

    pass

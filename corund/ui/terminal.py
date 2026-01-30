from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QLineEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from corund.ui.panels import GlassPanel
from corund.tools.router import ToolRouter

class TerminalPanel(GlassPanel):
    """
    A live shell terminal for Etherea.
    """
    def __init__(self, title="Terminal", parent=None):
        super().__init__(title=title, parent=parent)
        
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 10))
        self.output.setStyleSheet("background: rgba(0,0,0,50); color: #50fa7b; border: 1px solid rgba(0,255,255,30);")
        
        self.input = QLineEdit()
        self.input.setFont(QFont("Consolas", 10))
        self.input.setStyleSheet("background: rgba(0,0,0,80); color: white; border: none; padding: 5px;")
        self.input.setPlaceholderText("Enter command...")
        self.input.returnPressed.connect(self._run_command)
        
        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)
        
        ToolRouter.instance().command_completed.connect(self._on_command_done)

    def log_thought(self, text: str):
        """Render agent thoughts with a distinct teal style."""
        self.output.append(f"<i style='color: #8be9fd;'>[Agent] {text}</i>")
        self._scroll_to_bottom()

    def log_tool_call(self, data: dict):
        tool = data.get("tool", "TOOL")
        args = ", ".join([f"{k}={v}" for k, v in data.items() if k != "tool"])
        self.output.append(f"<b style='color: #50fa7b;'>▶ Calling {tool}:</b> <span style='color: #f1fa8c;'>{args}</span>")
        self._scroll_to_bottom()

    def log_tool_result(self, data: dict):
        success = data.get("success", False)
        color = "#50fa7b" if success else "#ff5555"
        status = "SUCCESS" if success else "FAILED"
        
        self.output.append(f"<b style='color: {color};'>◀ {data.get('tool', 'TOOL')} {status}</b>")
        
        stdout = data.get("stdout", "")
        stderr = data.get("stderr", "")
        
        if stdout:
            lines = stdout.splitlines()
            display_out = "\n".join(lines[:30])
            if len(lines) > 30: display_out += "\n... (output truncated)"
            self.output.append(f"<pre style='color: #f8f8f2; background: #282a36; padding: 5px;'>{display_out}</pre>")
        
        if stderr:
             self.output.append(f"<pre style='color: #ff5555;'>Err: {stderr}</pre>")
        
        if not stdout and not stderr:
            self.output.append("<i style='color: #6272a4;'>No stdout/stderr produced (command may still succeed).</i>")
        
        self._scroll_to_bottom()

    def log_result_card(self, card: dict):
        title = card.get("title", "TASK RESULT")
        status = card.get("status", "UNKNOWN")
        color = "#50fa7b" if status == "SUCCESS" else "#ff5555"
        
        html = f"""
        <div style='border: 2px solid {color}; padding: 10px; margin: 5px; border-radius: 8px; background: rgba(0,0,0,0.2);'>
            <h3 style='color: {color}; margin-top: 0;'>{title} — {status}</h3>
            <p style='color: #f8f8f2;'><b>Summary:</b> {card.get('summary', '')}</p>
            <p style='color: #8be9fd;'><b>Evidence:</b></p>
            <ul style='color: #bd93f9;'>
        """
        for item in card.get("evidence", []):
            html += f"<li>{item}</li>"
        html += f"""
            </ul>
            <p style='color: #ffb86c; font-size: 0.9em;'>Location: {card.get('location', '')}</p>
        </div>
        """
        self.output.append(html)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

    def _run_command(self):
        cmd = self.input.text()
        if not cmd: return
        self.output.append(f"\n<span style='color: #00f0ff;'>$ {cmd}</span>")
        self.input.clear()
        ToolRouter.instance().run_command(cmd)

    def _on_command_done(self, result: dict):
        """Render results for commands triggered from this panel or the router."""
        # Use the rich tool result logger for consistency
        self.log_tool_result({
            "tool": "SHELL",
            **result
        })

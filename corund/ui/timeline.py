from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QScrollBar
from corund.ui.panels import GlassPanel

class TimelinePanel(GlassPanel):
    """
    AGENT TIMELINE (Next 6)
    Structured surface for tracking agent thoughts and tool interactions.
    """
    def __init__(self, title="Agent Timeline", parent=None):
        super().__init__(title=title, parent=parent)
        
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background: transparent; color: #f8f8f2; border: none; font-family: 'Segoe UI', sans-serif;")
        
        # Enable rich HTML
        self.output.setAcceptRichText(True)
        
        self.layout.addWidget(self.output)

    def log_thought(self, text: str):
        """Render agent thoughts."""
        self.output.append(f"<div style='color: #8be9fd; margin-bottom: 5px;'>💭 <i>{text}</i></div>")
        self._scroll_to_bottom()

    def log_tool_call(self, data: dict):
        tool = data.get("tool", "TOOL")
        args = ", ".join([f"{k}={v}" for k, v in data.items() if k != "tool"])
        html = f"""
        <div style='background: rgba(80, 250, 123, 0.1); border-left: 3px solid #50fa7b; padding: 5px; margin-bottom: 5px;'>
            <b style='color: #50fa7b;'>▶ {tool}</b> <span style='color: #f1fa8c; font-size: 0.9em;'>{args}</span>
        </div>
        """
        self.output.append(html)
        self._scroll_to_bottom()

    def log_tool_result(self, data: dict):
        success = data.get("success", False)
        color = "#50fa7b" if success else "#ff5555"
        status = "SUCCESS" if success else "FAILED"
        
        html = f"""
        <div style='background: rgba({ '80, 250, 123' if success else '255, 85, 85'}, 0.05); border-left: 3px solid {color}; padding: 5px; margin-bottom: 10px;'>
            <b style='color: {color};'>◀ {data.get('tool', 'TOOL')} {status}</b>
        """
        
        stdout = data.get("stdout", "")
        stderr = data.get("stderr", "")
        
        if stdout:
            lines = stdout.splitlines()
            display_out = "\n".join(lines[:10]) # Shorter in timeline
            if len(lines) > 10: 
                display_out += "\n... (output truncated)"
            html += f"<pre style='color: #f8f8f2; font-size: 0.85em; margin: 5px 0;'>{display_out}</pre>"
            
        if stderr:
             html += f"<pre style='color: #ff5555; font-size: 0.85em;'>Err: {stderr}</pre>"

        if not stdout and not stderr:
            html += "<div style='color: #6272a4; font-size: 0.8em; font-style: italic;'>No stdout/stderr produced.</div>"
             
        html += "</div>"
        self.output.append(html)
        self._scroll_to_bottom()

    def log_result_card(self, card: dict):
        status = card.get("status", "UNKNOWN")
        color = "#50fa7b" if status == "SUCCESS" else "#ff5555"
        
        html = f"""
        <div style='border: 2px solid {color}; padding: 12px; margin: 10px 0; border-radius: 10px; background: rgba(0,0,0,0.3);'>
            <h3 style='color: {color}; margin: 0 0 8px 0;'>🏆 {card.get('title', 'TASK')} — {status}</h3>
            <p style='color: #f8f8f2; margin-bottom: 8px;'>{card.get('summary', '')}</p>
            <div style='color: #8be9fd; font-weight: bold; font-size: 0.9em;'>Evidence:</div>
            <ul style='color: #bd93f9; margin-top: 5px; margin-bottom: 8px; font-size: 0.9em;'>
        """
        for item in card.get("evidence", []):
            html += f"<li>{item}</li>"
        html += f"""
            </ul>
            <div style='color: #ff79c6; font-size: 0.8em; font-style: italic;'>Surface: {card.get('location', '')}</div>
        </div>
        """
        self.output.append(html)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

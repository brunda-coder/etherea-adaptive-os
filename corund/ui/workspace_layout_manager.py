from __future__ import annotations

class WorkspaceLayoutManager:
    """
    Controls workspace UI layout based on mode.
    SAFE DESIGN:
    - No widget deletion
    - Only show/hide or resize
    - Always reversible
    """

    def __init__(self, *, avatar_widget, console_widget, aurora_widget):
        self.avatar = avatar_widget
        self.console = console_widget
        self.aurora = aurora_widget

    def apply_layout(self, layout: str):
        layout = (layout or "").lower()

        if layout == "study":
            self._study_layout()
        elif layout == "coding":
            self._coding_layout()
        elif layout == "exam":
            self._exam_layout()
        elif layout == "calm":
            self._calm_layout()
        else:
            self._default_layout()

    # ---- Layout presets ----

    def _study_layout(self):
        # Balanced view
        self.avatar.show()
        self.aurora.show()
        self.console.show()

        self.avatar.setMinimumWidth(360)
        self.console.setMinimumHeight(220)

    def _coding_layout(self):
        # Console dominant
        self.avatar.show()
        self.aurora.hide()
        self.console.show()

        self.console.setMinimumHeight(420)

    def _exam_layout(self):
        # Minimal distractions
        self.avatar.hide()
        self.aurora.hide()
        self.console.show()

        self.console.setMinimumHeight(520)

    def _calm_layout(self):
        # Avatar + aurora only
        self.avatar.show()
        self.aurora.show()
        self.console.hide()

    def _default_layout(self):
        self.avatar.show()
        self.aurora.show()
        self.console.show()

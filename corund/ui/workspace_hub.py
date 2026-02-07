from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen, QTextCharFormat, QTextCursor, QSyntaxHighlighter
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSlider,
    QStackedWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class DrawingCanvas(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(280)
        self.setStyleSheet("background:#fff; border:1px solid #ccc;")
        self._pix = None
        self._last = None
        self.color = QColor("#222")
        self.size = 4
        self.eraser = False

    def _ensure(self):
        if self._pix is None:
            self._pix = self.grab().copy()
            self._pix.fill(Qt.white)

    def mousePressEvent(self, e):
        self._ensure()
        self._last = e.position().toPoint()

    def mouseMoveEvent(self, e):
        if self._last is None:
            return
        p = QPainter(self._pix)
        pen = QPen(Qt.white if self.eraser else self.color, self.size, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        cur = e.position().toPoint()
        p.drawLine(self._last, cur)
        p.end()
        self._last = cur
        self.update()

    def mouseReleaseEvent(self, e):
        self._last = None

    def paintEvent(self, e):
        self._ensure()
        p = QPainter(self)
        p.drawPixmap(0, 0, self._pix)

    def save_to(self, path: Path) -> Path:
        self._ensure()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._pix.save(str(path))
        return path


class PythonHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        fmt = QTextCharFormat(); fmt.setForeground(QColor("#8be9fd"))
        for kw in ["def", "class", "import", "from", "return", "if", "else", "for", "while"]:
            i = text.find(kw)
            while i >= 0:
                self.setFormat(i, len(kw), fmt)
                i = text.find(kw, i + len(kw))


class WorkspaceHubWidget(QFrame):
    def __init__(self, app_controller=None, parent=None) -> None:
        super().__init__(parent)
        self.app_controller = app_controller
        self.setProperty("panel", True)
        self.project_dir = Path("workspace/projects").resolve()
        self.current_file: Path | None = None

        layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        self.drawing_page = self._build_drawing_page()
        self.pdf_page = self._build_pdf_page()
        self.coding_page = self._build_coding_page()
        self.stack.addWidget(self.drawing_page)
        self.stack.addWidget(self.pdf_page)
        self.stack.addWidget(self.coding_page)
        layout.addWidget(self.stack)

    def set_mode(self, workspace_name: str) -> None:
        name = (workspace_name or "").lower()
        if "draw" in name:
            self.stack.setCurrentWidget(self.drawing_page)
        elif "pdf" in name or "document" in name:
            self.stack.setCurrentWidget(self.pdf_page)
        elif "cod" in name:
            self.stack.setCurrentWidget(self.coding_page)

    def _build_drawing_page(self) -> QWidget:
        w = QWidget(); l = QVBoxLayout(w)
        tools = QHBoxLayout()
        self.canvas = DrawingCanvas()
        save_btn = QPushButton("Save drawing")
        save_btn.clicked.connect(self._save_drawing)
        eraser_btn = QPushButton("Eraser")
        eraser_btn.clicked.connect(lambda: setattr(self.canvas, "eraser", not self.canvas.eraser))
        size = QSlider(Qt.Horizontal); size.setRange(1, 20); size.setValue(4); size.valueChanged.connect(lambda v: setattr(self.canvas, "size", v))
        tools.addWidget(save_btn); tools.addWidget(eraser_btn); tools.addWidget(QLabel("Size")); tools.addWidget(size)
        l.addLayout(tools); l.addWidget(self.canvas)
        return w

    def _build_pdf_page(self) -> QWidget:
        w = QWidget(); l = QVBoxLayout(w)
        row = QHBoxLayout()
        open_btn = QPushButton("Open PDF")
        open_btn.clicked.connect(self._open_pdf)
        summarize = QPushButton("Summarize")
        summarize.clicked.connect(self._summarize_pdf)
        row.addWidget(open_btn); row.addWidget(summarize)
        self.pdf_label = QLabel("No PDF loaded")
        self.pdf_notes = QTextEdit(); self.pdf_notes.setPlaceholderText("Add annotation notes…")
        self.pdf_summary = QTextEdit(); self.pdf_summary.setReadOnly(True)
        l.addLayout(row); l.addWidget(self.pdf_label); l.addWidget(self.pdf_notes); l.addWidget(self.pdf_summary)
        return w

    def _build_coding_page(self) -> QWidget:
        w = QWidget(); l = QHBoxLayout(w)
        self.file_tree = QTreeWidget(); self.file_tree.setHeaderLabel("Files")
        self.file_tree.itemClicked.connect(self._open_tree_file)
        left = QVBoxLayout(); new_btn = QPushButton("New file"); save_btn = QPushButton("Save")
        new_btn.clicked.connect(self._new_file); save_btn.clicked.connect(self._save_file)
        left.addWidget(new_btn); left.addWidget(save_btn); left.addWidget(self.file_tree)
        leftw = QWidget(); leftw.setLayout(left)
        self.code_editor = QTextEdit(); PythonHighlighter(self.code_editor.document())
        l.addWidget(leftw, 1); l.addWidget(self.code_editor, 3)
        self._refresh_tree()
        return w

    def _save_drawing(self) -> None:
        out = self.canvas.save_to(self.project_dir / "drawing_latest.png")
        QMessageBox.information(self, "Drawing saved", str(out))

    def _open_pdf(self) -> None:
        fp, _ = QFileDialog.getOpenFileName(self, "Open PDF", str(Path.home()), "PDF Files (*.pdf)")
        if fp:
            self.pdf_label.setText(fp)

    def _summarize_pdf(self) -> None:
        summary = {
            "file": self.pdf_label.text(),
            "annotation": self.pdf_notes.toPlainText()[:200],
            "summary": "Stub summary: key points extracted.",
            "action_items": ["Review section 2", "Create follow-up notes"],
        }
        self.pdf_summary.setPlainText(json.dumps(summary, indent=2))

    def _refresh_tree(self) -> None:
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.file_tree.clear()
        for f in sorted(self.project_dir.rglob("*")):
            if f.is_file():
                self.file_tree.addTopLevelItem(QTreeWidgetItem([str(f.relative_to(self.project_dir))]))

    def _new_file(self) -> None:
        fp, _ = QFileDialog.getSaveFileName(self, "Create file", str(self.project_dir), "All (*.*)")
        if fp:
            Path(fp).write_text("", encoding="utf-8")
            self.current_file = Path(fp)
            self._refresh_tree()

    def _open_tree_file(self, item):
        p = self.project_dir / item.text(0)
        self.current_file = p
        self.code_editor.setPlainText(p.read_text(encoding="utf-8", errors="ignore"))

    def _save_file(self) -> None:
        if not self.current_file:
            self._new_file()
        if self.current_file:
            self.current_file.write_text(self.code_editor.toPlainText(), encoding="utf-8")
            self._refresh_tree()

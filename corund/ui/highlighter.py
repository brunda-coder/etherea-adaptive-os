from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#ff79c6")) # Pink
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "class", "continue", "def", "del", "elif", "else", "except",
            "finally", "for", "from", "global", "if", "import", "in", "is",
            "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
            "while", "with", "yield"
        ]
        for kw in keywords:
            rule = (QRegularExpression(f"\\b{kw}\\b"), keyword_format)
            self.rules.append(rule)

        # Builtins
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#8be9fd")) # Cyan
        rule = (QRegularExpression(f"\\b(print|len|range|self|cls)\\b"), builtin_format)
        self.rules.append(rule)

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#f1fa8c")) # Yellow
        self.rules.append((QRegularExpression("\".*\""), string_format))
        self.rules.append((QRegularExpression("'.*'"), string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6272a4")) # Muted Blue/Grey
        self.rules.append((QRegularExpression("#.*"), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.rules:
            expression = QRegularExpression(pattern)
            it = expression.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

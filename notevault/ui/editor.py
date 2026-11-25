"""Редактор Markdown с подсветкой основных конструкций."""
import re

from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat
from PySide6.QtWidgets import QPlainTextEdit

from notevault.core.note import TAG_RE, WIKILINK_RE


class MarkdownHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        for pattern, color in (
            (re.compile(r"^#{1,6}\s.*"), "#865238"),
            (WIKILINK_RE, "#23786d"),
            (TAG_RE, "#816329"),
            (re.compile(r"`[^`]+`"), "#835692"),
        ):
            style = QTextCharFormat()
            style.setForeground(QColor(color))
            for match in pattern.finditer(text):
                self.setFormat(match.start(), len(match[0]), style)


class Editor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.highlighter = MarkdownHighlighter(self.document())
        self.setPlaceholderText("Начните писать в Markdown…")

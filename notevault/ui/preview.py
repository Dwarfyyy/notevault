"""Предпросмотр Markdown с переходами по wiki-ссылкам."""
import re
from urllib.parse import quote, unquote

from PySide6.QtCore import Signal
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QTextBrowser

from notevault.core.note import CODE_BLOCK_RE, INLINE_CODE_RE, WIKILINK_RE


class Preview(QTextBrowser):
    navigate = Signal(str)

    def __init__(self):
        super().__init__()
        self.setOpenLinks(False)
        self.anchorClicked.connect(self.follow)

    def follow(self, url):
        destination = url.toString()
        if destination.startswith("note:"):
            self.navigate.emit(unquote(destination[5:]))

    def render(self, text):
        def wiki_link(match):
            target = match[1].strip()
            label = (match[2] or target).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
            return f"[{label}](note:{quote(target, safe='')})"

        parts = re_split_code(text)
        for index in range(0, len(parts), 2):
            parts[index] = WIKILINK_RE.sub(wiki_link, parts[index])
        self.document().setMarkdown("".join(parts), QTextDocument.MarkdownFeature.MarkdownDialectGitHub |
                                    QTextDocument.MarkdownFeature.MarkdownNoHTML)


def re_split_code(text):
    return re.split(f"({CODE_BLOCK_RE.pattern}|{INLINE_CODE_RE.pattern})", text, flags=re.DOTALL)

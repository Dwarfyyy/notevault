"""Полнотекстовый поиск по хранилищу."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .note import Note
from .vault import Vault

CONTEXT_CHARS = 60


@dataclass
class SearchHit:
    """Одно совпадение: заметка, номер строки и контекст."""

    note: Note
    line_no: int
    line: str
    start: int
    end: int

    @property
    def context(self) -> str:
        left = self.line[max(0, self.start - CONTEXT_CHARS):self.start]
        match = self.line[self.start:self.end]
        right = self.line[self.end:self.end + CONTEXT_CHARS]
        return f"…{left}**{match.strip()}**{right}…"


def search(vault: Vault, query: str, *, regex: bool = False,
           case_sensitive: bool = False) -> list[SearchHit]:
    """Ищет подстроку (или регулярное выражение) во всех заметках."""
    if not query:
        return []
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = query if regex else re.escape(query)
    try:
        rx = re.compile(pattern, flags)
    except re.error:
        return []

    hits: list[SearchHit] = []
    for note in vault.notes.values():
        for line_no, line in enumerate(note.text.splitlines(), start=1):
            for match in rx.finditer(line):
                hits.append(SearchHit(note, line_no, line,
                                      match.start(), match.end()))
    return hits


def search_titles(vault: Vault, query: str) -> list[Note]:
    """Быстрый поиск по именам заметок (для палитры перехода)."""
    query = query.casefold()
    return [n for n in vault.all_notes() if query in n.name.casefold()]

"""Хранилище заметок (vault).

Хранилище — это папка с Markdown-файлами. Класс :class:`Vault` сканирует её,
держит индекс заметок и умеет создавать/переименовывать/удалять файлы.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from .note import Note, normalize_name


class Vault:
    """Папка с заметками и индекс по ним."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.notes: dict[str, Note] = {}  # нормализованное имя -> заметка
        self.reload()

    # ------------------------------------------------------------------ IO

    def reload(self) -> None:
        """Полностью пересканирует хранилище."""
        self.notes.clear()
        for path in sorted(self.root.rglob("*.md")):
            self._add(Note.load(path))

    def _add(self, note: Note) -> None:
        self.notes[normalize_name(note.name)] = note

    # -------------------------------------------------------------- запросы

    def get(self, name: str) -> Note | None:
        """Находит заметку по имени (без учёта регистра)."""
        return self.notes.get(normalize_name(name))

    def all_notes(self) -> list[Note]:
        return sorted(self.notes.values(), key=lambda n: n.name.casefold())

    def all_tags(self) -> dict[str, list[Note]]:
        """Индекс тегов: тег -> список заметок с этим тегом."""
        index: dict[str, list[Note]] = {}
        for note in self.notes.values():
            for tag in note.tags:
                index.setdefault(tag, []).append(note)
        return dict(sorted(index.items()))

    # ------------------------------------------------------------ изменения

    def note_path(self, name: str) -> Path:
        safe = name.strip().replace("/", "_").replace("\\", "_")
        return self.root / f"{safe}.md"

    def create(self, name: str, text: str = "") -> Note:
        """Создаёт новую заметку; если существует — возвращает её."""
        existing = self.get(name)
        if existing is not None:
            return existing
        note = Note(path=self.note_path(name), text=text)
        note.save()
        self._add(note)
        return note

    def create_daily(self, today: date | None = None) -> Note:
        """Создаёт (или открывает) ежедневную заметку на указанную дату."""
        today = today or date.today()
        name = today.strftime("%Y-%m-%d")
        note = self.get(name)
        if note is None:
            note = self.create(name, text=f"# {name}\n\n")
        return note

    def rename(self, note: Note, new_name: str) -> Note:
        """Переименовывает файл заметки и обновляет индекс."""
        old_key = normalize_name(note.name)
        new_path = self.note_path(new_name)
        note.path.rename(new_path)
        self.notes.pop(old_key, None)
        note.path = new_path
        self._add(note)
        return note

    def delete(self, note: Note) -> None:
        note.path.unlink(missing_ok=True)
        self.notes.pop(normalize_name(note.name), None)

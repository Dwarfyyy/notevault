"""Модель заметки и парсинг Markdown-разметки.

Заметка — это Markdown-файл внутри хранилища. Из текста извлекаются:
- wiki-ссылки:  ``[[Название заметки]]`` и ``[[Заметка|отображаемый текст]]``;
- теги:         ``#тег`` (включая вложенные вида ``#учёба/проекты``);
- заголовок:    первый заголовок ``# ...`` либо имя файла.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\[\]|]+)(?:\|([^\[\]]+))?\]\]")
TAG_RE = re.compile(r"(?<![\w/])#([\w/][\w/-]*)", re.UNICODE)
HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def strip_code(text: str) -> str:
    """Убирает блоки кода — ссылки и теги внутри них игнорируются."""
    text = CODE_BLOCK_RE.sub("", text)
    return INLINE_CODE_RE.sub("", text)


def parse_wikilinks(text: str) -> list[str]:
    """Возвращает список целей wiki-ссылок (без дублей, в порядке появления)."""
    targets: list[str] = []
    for match in WIKILINK_RE.finditer(strip_code(text)):
        target = match.group(1).strip()
        if target and target not in targets:
            targets.append(target)
    return targets


def parse_tags(text: str) -> list[str]:
    """Возвращает список тегов заметки (без символа #)."""
    tags: list[str] = []
    for match in TAG_RE.finditer(strip_code(text)):
        tag = match.group(1).rstrip(".,;:!?)")
        if tag and tag not in tags:
            tags.append(tag)
    return tags


def parse_title(text: str) -> str | None:
    """Первый заголовок верхнего уровня в тексте, если есть."""
    match = HEADING_RE.search(text)
    return match.group(1).strip() if match else None


def normalize_name(name: str) -> str:
    """Нормализует имя заметки для сравнения (регистр, пробелы)."""
    return " ".join(name.split()).casefold()


@dataclass
class Note:
    """Одна заметка в хранилище."""

    path: Path
    text: str = ""
    links: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.refresh()

    @property
    def name(self) -> str:
        """Имя заметки — имя файла без расширения."""
        return self.path.stem

    @property
    def title(self) -> str:
        """Заголовок из текста, иначе имя файла."""
        return parse_title(self.text) or self.name

    def refresh(self) -> None:
        """Пересчитывает ссылки и теги по текущему тексту."""
        self.links = parse_wikilinks(self.text)
        self.tags = parse_tags(self.text)

    @classmethod
    def load(cls, path: Path) -> "Note":
        return cls(path=path, text=path.read_text(encoding="utf-8"))

    def save(self, text: str | None = None) -> None:
        content = self.text if text is None else text
        self.path.write_text(content, encoding="utf-8")
        self.text = content
        self.refresh()

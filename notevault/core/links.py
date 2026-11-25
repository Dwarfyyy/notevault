"""Связи между заметками: исходящие ссылки и бэклинки."""
from __future__ import annotations

from .note import Note, normalize_name
from .vault import Vault


def outgoing_links(vault: Vault, note: Note) -> list[Note]:
    """Существующие заметки, на которые ссылается данная."""
    result = []
    for target in note.links:
        linked = vault.get(target)
        if linked is not None:
            result.append(linked)
    return result


def broken_links(vault: Vault, note: Note) -> list[str]:
    """Ссылки на ещё не созданные заметки («красные» ссылки)."""
    return [t for t in note.links if vault.get(t) is None]


def backlinks(vault: Vault, note: Note) -> list[Note]:
    """Заметки, которые ссылаются на данную (обратные ссылки)."""
    key = normalize_name(note.name)
    result = []
    for other in vault.notes.values():
        if other is note:
            continue
        if any(normalize_name(t) == key for t in other.links):
            result.append(other)
    return sorted(result, key=lambda n: n.name.casefold())


def link_suggestions(vault: Vault, prefix: str, limit: int = 10) -> list[str]:
    """Автодополнение имён заметок для ввода ``[[...``."""
    prefix = prefix.casefold()
    names = [n.name for n in vault.all_notes() if prefix in n.name.casefold()]
    return names[:limit]

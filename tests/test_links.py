import pytest

from notevault.core.links import backlinks, broken_links, link_suggestions, outgoing_links
from notevault.core.vault import Vault


@pytest.fixture
def vault(tmp_path):
    (tmp_path / "Алгоритмы.md").write_text(
        "# Алгоритмы\nСм. [[Сортировка]] и [[Несуществующая]]", encoding="utf-8")
    (tmp_path / "Сортировка.md").write_text(
        "# Сортировка\nЧасть [[Алгоритмы]]", encoding="utf-8")
    (tmp_path / "Python.md").write_text(
        "# Python\nДля [[Алгоритмы]] и [[Сортировка]]", encoding="utf-8")
    return Vault(tmp_path)


def test_outgoing_links(vault):
    note = vault.get("Алгоритмы")
    assert [n.name for n in outgoing_links(vault, note)] == ["Сортировка"]


def test_broken_links(vault):
    note = vault.get("Алгоритмы")
    assert broken_links(vault, note) == ["Несуществующая"]


def test_backlinks(vault):
    note = vault.get("Алгоритмы")
    assert {n.name for n in backlinks(vault, note)} == {"Сортировка", "Python"}


def test_backlinks_case_insensitive(vault):
    note = vault.get("сортировка")  # регистр не важен
    assert note is not None
    assert {n.name for n in backlinks(vault, note)} == {"Алгоритмы", "Python"}


def test_link_suggestions(vault):
    assert link_suggestions(vault, "сорт") == ["Сортировка"]
    assert len(link_suggestions(vault, "")) == 3

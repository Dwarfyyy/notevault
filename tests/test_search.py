import pytest

from notevault.core.search import search, search_titles
from notevault.core.vault import Vault


@pytest.fixture
def vault(tmp_path):
    (tmp_path / "a.md").write_text("Привет, мир!\nВторая строка про мир",
                                   encoding="utf-8")
    (tmp_path / "b.md").write_text("Ничего не совпадает", encoding="utf-8")
    return Vault(tmp_path)


def test_search_finds_all_hits(vault):
    hits = search(vault, "мир")
    assert len(hits) == 2
    assert all(h.note.name == "a" for h in hits)
    assert {h.line_no for h in hits} == {1, 2}


def test_search_case_insensitive(vault):
    assert len(search(vault, "ПРИВЕТ")) == 1
    assert len(search(vault, "ПРИВЕТ", case_sensitive=True)) == 0


def test_search_regex(vault):
    assert len(search(vault, r"мир\w*", regex=True)) == 2


def test_search_empty_and_invalid(vault):
    assert search(vault, "") == []
    assert search(vault, "(", regex=True) == []  # битое регулярное выражение


def test_search_titles(vault):
    assert [n.name for n in search_titles(vault, "a")] == ["a"]
    assert search_titles(vault, "zzz") == []

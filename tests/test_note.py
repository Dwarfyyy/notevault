from notevault.core.note import Note, parse_tags, parse_title, parse_wikilinks


def test_parse_wikilinks_simple():
    assert parse_wikilinks("См. [[Python]] и [[Заметка 2]]") == ["Python", "Заметка 2"]


def test_parse_wikilinks_with_alias():
    assert parse_wikilinks("[[Python|язык Python]]") == ["Python"]


def test_parse_wikilinks_no_duplicates():
    assert parse_wikilinks("[[A]] текст [[A]]") == ["A"]


def test_links_in_code_are_ignored():
    text = "Реальная [[ссылка]]\n```\n[[не ссылка]]\n```\n`[[тоже нет]]`"
    assert parse_wikilinks(text) == ["ссылка"]


def test_parse_tags():
    assert parse_tags("Заметка #учёба и #проекты/2026, ещё #учёба") == ["учёба", "проекты/2026"]


def test_parse_title():
    assert parse_title("текст\n# Мой заголовок\nещё текст") == "Мой заголовок"
    assert parse_title("без заголовка") is None


def test_note_refresh(tmp_path):
    note = Note(path=tmp_path / "a.md", text="# A\n[[B]] #тег")
    assert note.title == "A"
    assert note.links == ["B"]
    assert note.tags == ["тег"]

    note.save("[[C]]")
    assert note.links == ["C"]
    assert (tmp_path / "a.md").read_text(encoding="utf-8") == "[[C]]"

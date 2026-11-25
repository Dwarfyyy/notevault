import pytest

from notevault.core.vault import Vault


def test_sanitized_name_does_not_overwrite_existing_note(tmp_path):
    vault = Vault(tmp_path)
    note = vault.create("Тема_Неделя", "исходный текст")
    assert vault.create("Тема/Неделя", "другой текст") is note
    assert note.path.read_text(encoding="utf-8") == "исходный текст"


def test_rename_conflict_preserves_both_notes(tmp_path):
    vault = Vault(tmp_path)
    first = vault.create("Первая", "один")
    second = vault.create("Вторая", "два")

    with pytest.raises(FileExistsError):
        vault.rename(first, "вторая")

    assert first.path.read_text(encoding="utf-8") == "один"
    assert second.path.read_text(encoding="utf-8") == "два"

"""Ядро NoteVault: модели и логика, не зависящие от GUI."""

from .note import Note
from .vault import Vault

__all__ = ["Note", "Vault"]

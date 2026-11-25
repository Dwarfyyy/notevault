"""Главное окно NoteVault."""
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QInputDialog, QLabel, QListWidget, QMainWindow, QMessageBox,
    QSplitter, QToolBar, QVBoxLayout, QWidget,
)

from notevault.core.vault import Vault
from .editor import Editor
from .preview import Preview


class Window(QMainWindow):
    def __init__(self, vault):
        super().__init__()
        self.vault = vault
        self.note = None
        self.setWindowTitle("NoteVault")
        self.resize(1160, 720)
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #f6f2e9; color: #272d27; }
            QPlainTextEdit, QTextBrowser, QListWidget, QLineEdit, QComboBox {
                background: #fffdf7; border: 1px solid #ddd6c6; border-radius: 5px;
                padding: 7px; selection-background-color: #25695e;
            }
            QToolBar { padding: 7px; spacing: 10px; }
            QLabel { padding: 5px; font-weight: bold; }
        """)

        self.toolbar = QToolBar("Заметки")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        self.action("Новая", self.new_note, "Ctrl+N")
        self.action("Сохранить", self.save, "Ctrl+S")
        self.action("Сегодня", self.daily)

        self.notes = QListWidget()
        self.notes.itemActivated.connect(lambda item: self.open_name(item.text()))
        self.notes.itemClicked.connect(lambda item: self.open_name(item.text()))
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.addWidget(QLabel("Хранилище"))
        self.sidebar_layout.addWidget(self.notes, 1)

        self.editor = Editor()
        self.editor.setEnabled(False)
        self.preview = Preview()
        self.preview.navigate.connect(self.open_name)
        self.editor.textChanged.connect(self.update_preview)
        self.panes = QSplitter(Qt.Orientation.Horizontal)
        for panel in (self.sidebar, self.editor, self.preview):
            self.panes.addWidget(panel)
        self.panes.setSizes([240, 460, 460])
        self.setCentralWidget(self.panes)

        self.refresh()
        if vault.get("Старт"):
            self.open_name("Старт")

    def action(self, label, callback, shortcut=None):
        action = QAction(label, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        self.toolbar.addAction(action)

    def refresh(self):
        self.notes.clear()
        for note in self.vault.all_notes():
            self.notes.addItem(note.name)
            if note is self.note:
                self.notes.setCurrentRow(self.notes.count() - 1)

    def update_preview(self):
        self.preview.render(self.editor.toPlainText())

    def save(self):
        if self.note is None or not self.editor.document().isModified():
            return True
        try:
            self.note.save(self.editor.toPlainText())
        except OSError as error:
            QMessageBox.warning(self, "Ошибка сохранения", str(error))
            return False
        self.editor.document().setModified(False)
        self.statusBar().showMessage("Заметка сохранена", 2500)
        return True

    def open_name(self, name):
        note = self.vault.get(name)
        if note is None:
            self.statusBar().showMessage(f"Заметка «{name}» не найдена", 3500)
            return
        if note is self.note or not self.save():
            return
        self.note = note
        self.editor.setEnabled(True)
        with QSignalBlocker(self.editor):
            self.editor.setPlainText(note.text)
        self.update_preview()
        self.setWindowTitle(f"{note.name} · NoteVault")
        self.refresh()

    def new_note(self):
        name, accepted = QInputDialog.getText(self, "Новая заметка", "Имя файла")
        if not accepted or not name.strip() or not self.save():
            return
        try:
            note = self.vault.create(name, f"# {name.strip()}\n\n")
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Ошибка создания", str(error))
            return
        self.open_name(note.name)
        self.editor.setFocus()

    def daily(self):
        if not self.save():
            return
        try:
            note = self.vault.create_daily()
        except OSError as error:
            QMessageBox.warning(self, "Ошибка создания", str(error))
            return
        self.open_name(note.name)

    def closeEvent(self, event):
        if self.save():
            event.accept()
        else:
            event.ignore()


def run(path):
    app = QApplication([])
    window = Window(Vault(path))
    window.show()
    return app.exec()

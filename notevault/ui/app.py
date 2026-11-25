"""Главное окно NoteVault."""
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QInputDialog, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMessageBox,
    QSplitter, QToolBar, QVBoxLayout, QWidget,
)

from notevault.core.links import backlinks
from notevault.core.search import search
from notevault.core.vault import Vault
from .editor import Editor
from .graph_view import GraphView
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
        self.action("Граф", self.show_graph)

        self.notes = QListWidget()
        self.notes.itemActivated.connect(self.open_result)
        self.notes.itemClicked.connect(self.open_result)
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.addWidget(QLabel("Хранилище"))
        self.query = QLineEdit()
        self.query.setPlaceholderText("Поиск по заметкам")
        self.query.textChanged.connect(self.refresh)
        self.tag = QComboBox()
        self.tag.currentIndexChanged.connect(self.refresh)
        self.sidebar_layout.addWidget(self.query)
        self.sidebar_layout.addWidget(self.tag)
        self.sidebar_layout.addWidget(self.notes, 3)
        self.sidebar_layout.addWidget(QLabel("Обратные ссылки"))
        self.incoming = QListWidget()
        self.incoming.itemClicked.connect(lambda item: self.open_name(item.text()))
        self.incoming.itemActivated.connect(lambda item: self.open_name(item.text()))
        self.sidebar_layout.addWidget(self.incoming, 1)

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
        first = vault.get("Старт") or next(iter(vault.all_notes()), None)
        if first is not None:
            self.open_name(first.name)

    def action(self, label, callback, shortcut=None):
        action = QAction(label, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        self.toolbar.addAction(action)

    def refresh(self):
        selected_tag = self.tag.currentData()
        with QSignalBlocker(self.tag):
            self.tag.clear()
            self.tag.addItem("Все теги", None)
            for tag in self.vault.all_tags():
                self.tag.addItem(f"#{tag}", tag)
            self.tag.setCurrentIndex(max(0, self.tag.findData(selected_tag)))
        selected_tag = self.tag.currentData()

        self.notes.clear()
        query = self.query.text().strip()
        if query:
            for hit in search(self.vault, query):
                if selected_tag is None or selected_tag in hit.note.tags:
                    context = hit.context.replace("**", "")
                    self.add_result(hit.note, f"{hit.note.name}:{hit.line_no}  {context}", hit.line_no)
        else:
            for note in self.vault.all_notes():
                if selected_tag is None or selected_tag in note.tags:
                    self.add_result(note, note.name)

        self.incoming.clear()
        if self.note is not None:
            self.incoming.addItems([note.name for note in backlinks(self.vault, self.note)])

    def add_result(self, note, label, line=None):
        item = QListWidgetItem(label)
        item.setData(Qt.ItemDataRole.UserRole, (note.name, line))
        self.notes.addItem(item)
        if note is self.note and line is None:
            self.notes.setCurrentItem(item)

    def open_result(self, item):
        name, line = item.data(Qt.ItemDataRole.UserRole)
        self.open_name(name)
        if line and self.note is self.vault.get(name):
            cursor = self.editor.textCursor()
            block = self.editor.document().findBlockByNumber(line - 1)
            if block.isValid():
                cursor.setPosition(block.position())
            self.editor.setTextCursor(cursor)
            self.editor.centerCursor()
            self.editor.setFocus()

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
        self.refresh()
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

    def show_graph(self):
        if not self.save():
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Граф заметок")
        dialog.resize(740, 560)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Двойной щелчок открывает заметку. Колесо меняет масштаб."))
        graph = GraphView(self.vault)
        layout.addWidget(graph)

        def open_node(name):
            self.open_name(name)
            dialog.accept()

        graph.navigate.connect(open_node)
        dialog.exec()

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

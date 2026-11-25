"""Граф wiki-ссылок с переходом к заметке."""
from math import cos, pi, sin

from PySide6.QtCore import QPointF, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from notevault.core.links import outgoing_links


class GraphView(QGraphicsView):
    navigate = Signal(str)

    def __init__(self, vault):
        super().__init__()
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        scene = QGraphicsScene(self)
        self.setScene(scene)
        notes = vault.all_notes()
        radius = max(120, len(notes) * 18)
        positions = {}
        for index, note in enumerate(notes):
            angle = index * 2 * pi / len(notes) - pi / 2
            positions[note.name] = QPointF(radius * cos(angle), radius * sin(angle))

        for note in notes:
            source = positions[note.name]
            for target in outgoing_links(vault, note):
                destination = positions[target.name]
                if source != destination:
                    scene.addLine(source.x(), source.y(), destination.x(), destination.y(),
                                  QPen(QColor("#a69d89")))

        for name, point in positions.items():
            marker = scene.addEllipse(point.x() - 7, point.y() - 7, 14, 14,
                                      QPen(QColor("#18564c")), QBrush(QColor("#398e7d")))
            label = scene.addSimpleText(name)
            label.setPos(point.x() + 11, point.y() - label.boundingRect().height() / 2)
            marker.setData(0, name)
            label.setData(0, name)
        if not notes:
            scene.addSimpleText("Создайте заметки и свяжите их через [[wiki-ссылки]].")
        scene.setSceneRect(scene.itemsBoundingRect().adjusted(-35, -35, 35, 35))

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        if item is not None and item.data(0):
            self.navigate.emit(item.data(0))
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        if not event.angleDelta().y():
            return super().wheelEvent(event)
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        if 0.2 <= self.transform().m11() * factor <= 5:
            self.scale(factor, factor)
        event.accept()

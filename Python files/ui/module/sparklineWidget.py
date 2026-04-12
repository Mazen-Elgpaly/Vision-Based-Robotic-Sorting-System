# ─────────────────────────────────────────────
#  LATENCY SPARKLINE CARD
# ─────────────────────────────────────────────
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QPainter, QPen
from ui.style.colors import Colors

class SparklineWidget(QWidget):
    def __init__(self, history):
        super().__init__()
        self.history = history

    def paintEvent(self, event):
        if len(self.history) < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        mn, mx = min(self.history), max(self.history)
        rng = mx - mn if mx != mn else 1

        pen = QPen(QColor(Colors.PRIMARY), 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        pts = []
        for i, v in enumerate(self.history):
            x = int(i * (w - 2) / (len(self.history) - 1)) + 1
            y = int((1 - (v - mn) / rng) * (h - 4)) + 2
            pts.append(QPoint(x, y))

        for i in range(len(pts) - 1):
            painter.drawLine(pts[i], pts[i+1])

        painter.end()

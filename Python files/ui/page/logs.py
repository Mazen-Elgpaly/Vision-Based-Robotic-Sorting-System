# ─────────────────────────────────────────────
#  Logs Page
# ─────────────────────────────────────────────

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton
from ui.style.colors import Colors
from PyQt5.QtCore import Qt


class LogsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("logs")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        label = QLabel("Logs Page")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Calibri", 12))
        label.setStyleSheet(f"color: {Colors.ON_SURFACE}; background: transparent;")
        layout.addWidget(label)
        # Here you can add buttons or controls for manual operation
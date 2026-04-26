# ─────────────────────────────────────────────
#  LATENCY SPARKLINE CARD
# ─────────────────────────────────────────────
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from ui.style.colors import Colors
from ui.module.sparklineWidget import SparklineWidget

class LatencyCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("card")
        self.setFixedHeight(112)
        self.history = [12, 15, 11, 18, 14, 12, 16, 13, 10, 12]

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        left = QVBoxLayout()
        left.setSpacing(4)
        lbl = QLabel("NETWORK LATENCY")
        lbl.setStyleSheet(f"color: {Colors.ON_SURF_VAR}; font-size: 8px; letter-spacing: 2px; background: transparent;")
        self.val_lbl = QLabel("12 ms")
        self.val_lbl.setStyleSheet(f"color: {Colors.ON_SURFACE}; font-size: 22px; font-weight: 700; font-family: Courier New; background: transparent;")
        left.addWidget(lbl)
        left.addStretch()
        left.addWidget(self.val_lbl)
        layout.addLayout(left)
        layout.addStretch()

        self.sparkline = SparklineWidget(self.history)
        self.sparkline.setFixedSize(750, 32)
        self.sparkline.setStyleSheet(f"background: transparent;")
        layout.addWidget(self.sparkline, 0, Qt.AlignVCenter)

    def update_value(self, latency):
        self.history.append(latency)
        if len(self.history) > 15:
            self.history.pop(0)
        self.val_lbl.setText(f"{latency} ms")
        self.sparkline.history = self.history
        self.sparkline.update()

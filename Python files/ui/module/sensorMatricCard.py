# ─────────────────────────────────────────────
#  SENSOR METRIC CARD
# ─────────────────────────────────────────────
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from ui.style.colors import Colors

class MetricCard(QFrame):
    def __init__(self, icon, value, unit, label, accent=Colors.PRIMARY, border_bottom=False):
        super().__init__()
        self.setObjectName("card")
        self.setFixedHeight(112)
        if border_bottom:
            self.setStyleSheet(f"""
                QFrame#card {{
                    background: {Colors.SURFACE_HIGH};
                    border-radius: 12px;
                    border: 1px solid rgba(93,216,226,0.06);
                    border-bottom: 2px solid {Colors.PRIMARY};
                }}
            """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"color: {accent}; font-size: 18px; background: transparent;")
        layout.addWidget(icon_lbl)
        layout.addStretch()

        self.val_lbl = QLabel(f"{value}")
        self.val_lbl.setStyleSheet(f"color: {Colors.ON_SURFACE}; font-size: 22px; font-weight: 700; font-family: Courier New; background: transparent;")

        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet(f"color: {Colors.ON_SURF_VAR}; font-size: 12px; background: transparent;")

        val_row = QHBoxLayout()
        val_row.setSpacing(4)
        val_row.addWidget(self.val_lbl)
        val_row.addWidget(unit_lbl, 0, Qt.AlignBottom)
        val_row.addStretch()
        layout.addLayout(val_row)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"color: {Colors.ON_SURF_VAR}; font-size: 8px; letter-spacing: 2px; background: transparent;")
        layout.addWidget(lbl)

    def update_value(self, value):
        self.val_lbl.setText(str(value))

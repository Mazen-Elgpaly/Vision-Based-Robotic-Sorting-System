# ─────────────────────────────────────────────
#  SYSTEM LOGS
# ─────────────────────────────────────────────
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QLabel

class LogEntry(QWidget):
    def __init__(self, timestamp, tag, tag_color, message, opacity=1.0):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(2)

        header = QHBoxLayout()
        ts_lbl = QLabel(timestamp)
        ts_lbl.setStyleSheet(f"color: rgba(93,216,226,0.6); font-size: 9px; font-family: Courier New; background: transparent;")

        tag_lbl = QLabel(f" {tag} ")
        tag_lbl.setStyleSheet(f"""
            color: {tag_color};
            background: transparent;
            border: 1px solid {tag_color};
            border-radius: 2px;
            font-size: 7px;
            letter-spacing: 1px;
            padding: 0px 2px;
        """)
        header.addWidget(ts_lbl)
        header.addStretch()
        header.addWidget(tag_lbl)
        layout.addLayout(header)

        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet(f"color: rgba(226,226,229,{opacity}); font-size: 11px; background: transparent;")
        msg_lbl.setWordWrap(True)
        layout.addWidget(msg_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: rgba(62,73,74,0.3);")
        layout.addWidget(sep)


# ─────────────────────────────────────────────
#  SIDE NAV BAR
# ─────────────────────────────────────────────

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel, QPushButton
from ui.style.colors import Colors
from PyQt5.QtCore import Qt, pyqtSignal
from ui.utility.logger import logger
from ui.vision.camDetect import CameraFeedPanel


class SideNavBar(QFrame):
    navigate = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(80)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo block
        logo_widget = QWidget()
        logo_widget.setFixedHeight(90)
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 16, 0, 0)
        logo_layout.setSpacing(2)
        logo_layout.setAlignment(Qt.AlignHCenter)

        icon_frame = QFrame()
        icon_frame.setFixedSize(40, 40)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background: {Colors.SURFACE_CONT};
                border-radius: 10px;
                border: 1px solid {Colors.OUTLINE_VAR};
            }}
        """)
        icon_lbl = QLabel("⚙", icon_frame)
        icon_lbl.setStyleSheet(f"color: {Colors.PRIMARY}; font-size: 18px; background: transparent;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setGeometry(0, 0, 40, 40)

        id_lbl = QLabel("OP_01")
        id_lbl.setStyleSheet(f"""
            color: {Colors.ON_SURFACE};
            font-size: 8px;
            letter-spacing: 3px;
            font-weight: 600;
            background: transparent;
        """)
        id_lbl.setAlignment(Qt.AlignCenter)

        conn_lbl = QLabel("CONNECTED")
        conn_lbl.setStyleSheet(f"""
            color: {Colors.PRIMARY};
            font-size: 7px;
            font-weight: 700;
            letter-spacing: 1px;
            background: transparent;
        """)
        conn_lbl.setAlignment(Qt.AlignCenter)

        logo_layout.addWidget(icon_frame, 0, Qt.AlignHCenter)
        logo_layout.addWidget(id_lbl)
        logo_layout.addWidget(conn_lbl)
        layout.addWidget(logo_widget)

        # Nav items
        nav_items = [
            ("Dashboard", "⊞", True),
            ("Telemetry", "⟡", False),
            ("Manual", "◈", False),
            ("Diagnostics", "◉", False),
            ("Logs", "≡", False),
        ]

        self.buttons = []

        for name, icon, active in nav_items:
            btn = QPushButton(f"{icon}\n{name.upper()}")
            btn.setObjectName("nav_btn_active" if active else "nav_btn")
            btn.setFixedHeight(70)
            btn.setFixedWidth(80)
            btn.setFont(QFont("Calibri", 100, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)

            self.buttons.append(btn)

            # handler
            def handler(_, n=name, b=btn):
                self.set_active(b)
                if n == "Telemetry":
                    logger.add_log("INFO", "Capturing Telemetry Snapshot 📸")
                self.navigate.emit(n)
                logger.add_log("INFO", f"Navigate to {n} 🔥")


            btn.clicked.connect(handler)
            layout.addWidget(btn)

            # خلي أول زر active فعليًا
            if active:
                self.set_active(btn)

        layout.addStretch()

        # Emergency button
        emerg_widget = QWidget()
        emerg_layout = QVBoxLayout(emerg_widget)
        emerg_layout.setContentsMargins(13, 0, 13, 20)
        emerg_btn = QPushButton("⚠")
        emerg_btn.setObjectName("emergency")
        emerg_btn.setFixedSize(54, 54)
        emerg_btn.clicked.connect(lambda: exit(0))  # Placeholder for actual emergency stop action
        emerg_btn.setToolTip("EMERGENCY STOP")
        emerg_layout.addWidget(emerg_btn, 0, Qt.AlignHCenter)
        layout.addWidget(emerg_widget)

    def set_active(self, active_btn):
        for btn in self.buttons:
            btn.setObjectName("nav_btn")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        active_btn.setObjectName("nav_btn_active")
        active_btn.style().unpolish(active_btn)
        active_btn.style().polish(active_btn)
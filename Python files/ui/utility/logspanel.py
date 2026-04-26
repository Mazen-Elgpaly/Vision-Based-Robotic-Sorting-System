# ─────────────────────────────────────────────
#  SYSTEM LOGS PANEL
# ─────────────────────────────────────────────
import os
import random
from datetime import datetime
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy
from ui.style.colors import Colors
from ui.utility.logs import LogEntry
from ui.utility.logger import logger
# from ui.vision.camDetect import CameraFeedPanel


class SystemLogsPanel(QFrame):
    
    def __init__(self, redcount=0, bluecount=0, greencount=0, graycount=0):
        super().__init__()
        logger.log_signal.connect(self.sendLog) # ربط إشارة اللوج بالواجهة
        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        self.redcount = redcount
        self.bluecount = bluecount
        self.greencount = greencount
        self.graycount = graycount

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(44)
        header.setStyleSheet(f"""
            QFrame {{
                background: rgba(40,42,44,0.5);
                border-radius: 0px;
                border-bottom: 1px solid rgba(62,73,74,0.2);
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)

        h_icon = QLabel("≡")
        h_icon.setFixedWidth(16)
        h_icon.setAlignment(Qt.AlignCenter)
        h_icon.setCursor(Qt.PointingHandCursor)
        h_icon.mousePressEvent = lambda e: self.clear_logs()
        h_icon.setStyleSheet(f"color: {Colors.PRIMARY}; font-size: 14px; background: transparent;")
        h_title = QLabel("SYSTEM_LOGS")
        h_title.setStyleSheet(f"color: {Colors.ON_SURFACE}; font-size: 10px; font-weight: 700; letter-spacing: 3px; background: transparent;")
        rt_badge = QLabel("REAL-TIME")
        rt_badge.setStyleSheet(f"""
            color: {Colors.ON_SURF_VAR};
            background: {Colors.SURFACE_LOWEST};
            border-radius: 3px;
            font-size: 8px;
            letter-spacing: 1px;
            padding: 2px 6px;
        """)
        header_layout.addWidget(h_icon)
        header_layout.addSpacing(6)
        header_layout.addWidget(h_title)
        header_layout.addStretch()
        header_layout.addWidget(rt_badge)

        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        self.log_layout = QVBoxLayout(scroll_widget)
        self.log_layout.setContentsMargins(16, 8, 16, 8)
        self.log_layout.setSpacing(0)
        self.log_layout.setAlignment(Qt.AlignTop)

        self.logs = []

        # self.logs = [
        #     ("14:22:04.12", "INFO",   Colors.PRIMARY,          "Object detected in safety zone A-4. Re-calculating path trajectory.", 1.0),
        #     ("14:22:03.45", "ACTION", Colors.TERTIARY,          "Color identified: #33F4A1. Sorting action completed on sorter 02.", 1.0),
        #     ("14:21:58.88", "INFO",   Colors.PRIMARY,          "Calibration synchronized with auxiliary sensor hub.", 0.9),
        #     ("14:21:55.30", "INFO",   Colors.PRIMARY,          "Package 4402 successfully routed to Outbound Terminal.", 0.7),
        #     ("14:21:42.11", "INFO",   Colors.PRIMARY,          "System initialization sequence finalized. Handshake complete.", 0.5),
        # ]
        # self._render_logs()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        footer = QFrame()
        footer.setFixedHeight(42)
        footer.setStyleSheet(f"""
            QFrame {{
                background: {Colors.SURFACE_LOWEST};
                border-top: 1px solid rgba(62,73,74,0.2);
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 0, 16, 0)
        footer_cols = QHBoxLayout()
        footer_cols.setContentsMargins(0, 0, 0, 0)
        footer_cols.setSpacing(8)
        footer_layout.addLayout(footer_cols)
        footer_layout.setAlignment(Qt.AlignCenter)
        # footer_layout.addWidget(export_btn, 0, Qt.AlignCenter)
        export_btn = self.buildButton("↗  EXPORT SESSION DATA", self.export_logs)
        clear_btn = self.buildButton("🗑  Clear LOGS", self.clear_logs)
        refresh_btn = self.buildButton("⟳  Refresh COUNTS", self.refresh_logs)
        footer_cols.addWidget(export_btn, 0, Qt.AlignCenter)
        footer_cols.addWidget(clear_btn, 0, Qt.AlignCenter)
        footer_cols.addWidget(refresh_btn, 0, Qt.AlignCenter)
        footer_cols.addStretch()
        footer_layout.addStretch()
        
        layout.addWidget(footer)
        
        self.scroll_widget = scroll_widget
        
    def buildButton(self, text, callback):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)
        btn.setStyleSheet(f"""QPushButton {{background: transparent;color: rgba(93,216,226,0.6);font-size: 9px;letter-spacing: 2px;border: none;padding: 4px 8px;}}QPushButton:hover {{color: {Colors.PRIMARY};}}""")
        return btn
        
    def refresh_logs(self):
        logger.add_log("INFO", f"Detected {self.redcount} red, {self.bluecount} blue, {self.greencount} green, {self.graycount} box in Frame!")
        self._render_logs()
        
    def export_logs(self):
        with open("session_logs.txt", "w", encoding="utf-8") as f:
            f.write("Timestamp\t| \tTag\t\t| Message\n")
            f.write("-" * 50 + "\n")
            f.write("\n".join([f"{ts}\t| {tag}    \t| {msg}" for ts, tag, color, msg, op in self.logs]))
            f.write("\n")
        os.system("notepad session_logs.txt")
        
    def clear_logs(self):
        self.logs = []
        self._render_logs()
        logger.clear_logs()    

    def _render_logs(self):
        while self.log_layout.count():
            child = self.log_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        for ts, tag, color, msg, op in self.logs:
            entry = LogEntry(ts, tag, color, msg, op)
            self.log_layout.addWidget(entry)
    
    def sendLog(self, kind, color, text):
        now = datetime.now().strftime("%H:%M:%S.%f")[:11]
        self.logs.insert(0, (now, kind, color, text, 1.0))
        self.logs = [(ts, t, c, m, max(0.3, o - 0.15)) for ts, t, c, m, o in self.logs]
        # if len(self.logs) > 8:
        #     self.logs.pop()
        self._render_logs()
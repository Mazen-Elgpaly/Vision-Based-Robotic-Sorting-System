import sys
import random
from datetime import datetime
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy
from ui.style.colors import Colors
from ui.style.styleSheet import STYLESHEET
from ui.vision.camDetect import CameraFeedPanel

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame,
    QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    QThread, pyqtSignal, QPoint, QRect
)
from PyQt5.QtGui import (
    QColor, QPalette, QFont, QPainter,
    QPen, QBrush, QPixmap
)



# ─────────────────────────────────────────────
#  ANIMATED TOGGLE SWITCH
# ─────────────────────────────────────────────
class AnimatedToggle(QWidget):
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 26)
        self._checked = True
        self._position = 2  # Initialize _position first
        
        # Create animation after initializing _position
        self._animation = QPropertyAnimation(self, b"position")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def get_position(self):
        return self._position
    
    def set_position(self, value):
        self._position = value
        self.update()
        
    position = pyqtProperty(float, get_position, set_position)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        if self._checked:
            bg_color = QColor(Colors.PRIMARY)
        else:
            bg_color = QColor(Colors.SURFACE_HIGHEST)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 13, 13)
        
        # Knob
        knob_color = QColor(255, 255, 255)
        painter.setBrush(QBrush(knob_color))
        
        knob_x = int(self._position)
        painter.drawEllipse(knob_x, 2, 22, 22)
        
    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._animation.setStartValue(self._position)
        self._animation.setEndValue(26 if self._checked else 2)
        self._animation.start()
        self.toggled.emit(self._checked)
        
    def isChecked(self):
        return self._checked
        
    def setChecked(self, checked):
        self._checked = checked
        self._position = 26 if checked else 2
        self.update()


# ─────────────────────────────────────────────
#  ANIMATED MODE TOGGLE
# ─────────────────────────────────────────────
class AnimatedModeToggle(QWidget):
    mode_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 28)
        self._mode = "AUTO"  # "AUTO" or "MANUAL"
        self._indicator_position = 2  # Initialize first
        
        # Create animation after initializing _indicator_position
        self._animation = QPropertyAnimation(self, b"indicator_position")
        self._animation.setDuration(250)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.auto_rect = QRect(2, 2, 56, 24)
        self.manual_rect = QRect(62, 2, 56, 24)
        
    def get_indicator_position(self):
        return self._indicator_position
    
    def set_indicator_position(self, value):
        self._indicator_position = value
        self.update()
        
    indicator_position = pyqtProperty(float, get_indicator_position, set_indicator_position)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.setPen(QPen(QColor(Colors.OUTLINE_VAR), 1))
        painter.setBrush(QBrush(QColor(Colors.SURFACE_LOWEST)))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 6, 6)
        
        # Indicator (moving blue box)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(Colors.PRIMARY)))
        indicator_x = int(self._indicator_position)
        painter.drawRoundedRect(indicator_x, 2, 56, 24, 4, 4)
        
        # Text
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        
        # AUTO text
        if self._mode == "AUTO":
            painter.setPen(QPen(QColor(Colors.ON_PRIMARY)))
        else:
            painter.setPen(QPen(QColor(Colors.ON_SURF_VAR)))
        painter.drawText(self.auto_rect, Qt.AlignCenter, "AUTO")
        
        # MANUAL text
        if self._mode == "MANUAL":
            painter.setPen(QPen(QColor(Colors.ON_PRIMARY)))
        else:
            painter.setPen(QPen(QColor(Colors.ON_SURF_VAR)))
        painter.drawText(self.manual_rect, Qt.AlignCenter, "MANUAL")
        
    def mousePressEvent(self, event):
        if self.auto_rect.contains(event.pos()):
            self.setMode("AUTO")
        elif self.manual_rect.contains(event.pos()):
            self.setMode("MANUAL")
            
    def setMode(self, mode):
        if self._mode != mode:
            self._mode = mode
            self._animation.setStartValue(self._indicator_position)
            self._animation.setEndValue(2 if mode == "AUTO" else 62)
            self._animation.start()
            self.mode_changed.emit(mode)
            self.update()
            
    def getMode(self):
        return self._mode


# ─────────────────────────────────────────────
#  LIVE TICKER: simulates real-time data
# ─────────────────────────────────────────────
class LiveDataThread(QThread):
    data_updated = pyqtSignal(dict)

    def run(self):
        while True:
            data = {
                "x_axis":     round(random.uniform(130, 160), 2),
                "y_axis":     round(random.uniform(-20, 10), 2),
                "load":       random.randint(50, 85),
                "temp":       round(random.uniform(32, 38), 1),
                "battery":    random.randint(80, 95),
                "latency":    random.randint(8, 25),
            }
            self.data_updated.emit(data)
            self.msleep(1200)


# ─────────────────────────────────────────────
#  SIDE NAV BAR
# ─────────────────────────────────────────────
class SideNavBar(QFrame):
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

        for name, icon, active in nav_items:
            btn = QPushButton(f"{icon}\n{name.upper()}")
            btn.setObjectName("nav_btn_active" if active else "nav_btn")
            btn.setFixedHeight(70)
            btn.setFixedWidth(80)
            btn.setFont(QFont("Calbiri", 90))
            layout.addWidget(btn)

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


# ─────────────────────────────────────────────
#  TOP BAR
# ─────────────────────────────────────────────
class TopBar(QFrame):
    mode_changed = pyqtSignal(str)
    wireless_changed = pyqtSignal(bool)
    power_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("topbar")
        self.setFixedHeight(64)
        
        self.power_on = True
        self.wireless_on = True

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        # Title
        title = QLabel("Vision-Based Robotic Arm V1.0")
        title.setStyleSheet(f"""
            color: {Colors.PRIMARY};
            font-size: 16px;
            font-weight: 700;
            letter-spacing: -1px;
            font-family: 'Courier New';
            background: transparent;
        """)
        layout.addWidget(title)
        layout.addStretch()

        # Toggle group
        toggle_frame = QFrame()
        toggle_frame.setStyleSheet(f"""
            QFrame {{
                background: {Colors.SURFACE_CONT};
                border-radius: 8px;
                border: 1px solid rgba(63,73,74,0.4);
            }}
        """)
        toggle_layout = QHBoxLayout(toggle_frame)
        toggle_layout.setContentsMargins(12, 6, 12, 6)
        toggle_layout.setSpacing(16)

        # Power with animated toggle
        power_lbl = QLabel("POWER")
        power_lbl.setStyleSheet(f"color: {Colors.ON_SURF_VAR}; font-size: 8px; letter-spacing: 2px; background: transparent;")
        toggle_layout.addWidget(power_lbl)
        
        self.power_toggle = AnimatedToggle()
        self.power_toggle.toggled.connect(self._on_power_toggled)
        toggle_layout.addWidget(self.power_toggle)
        
        self._add_divider(toggle_layout)
        
        # Mode with animated toggle
        mode_lbl = QLabel("MODE")
        mode_lbl.setStyleSheet(f"color: {Colors.ON_SURF_VAR}; font-size: 8px; letter-spacing: 2px; background: transparent;")
        toggle_layout.addWidget(mode_lbl)
        
        self.mode_toggle = AnimatedModeToggle()
        self.mode_toggle.mode_changed.connect(self._on_mode_changed)
        toggle_layout.addWidget(self.mode_toggle)
        
        self._add_divider(toggle_layout)
        
        # Wireless button
        self.wireless_btn = QPushButton()
        self.wireless_btn.setCursor(Qt.PointingHandCursor)
        self.wireless_btn.clicked.connect(self._toggle_wireless)
        self._update_wireless_style()
        toggle_layout.addWidget(self.wireless_btn)

        layout.addWidget(toggle_frame)
        layout.addSpacing(16)

        # Icons
        for icon in ["⌨", "⚙", "?"]:
            btn = QLabel(icon)
            btn.setStyleSheet(f"color: rgba(93,216,226,0.6); font-size: 16px; background: transparent;")
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)
            layout.addSpacing(8)
    
    def _on_power_toggled(self, checked):
        self.power_on = checked
        self.power_changed.emit(checked)
    
    def _on_mode_changed(self, mode):
        self.mode_changed.emit(mode)
    
    def _toggle_wireless(self):
        self.wireless_on = not self.wireless_on
        self._update_wireless_style()
        self.wireless_changed.emit(self.wireless_on)
    
    def _update_wireless_style(self):
        if self.wireless_on:
            self.wireless_btn.setText("📶 WIRELESS")
            self.wireless_btn.setStyleSheet(f"""
                QPushButton {{
                    color: {Colors.PRIMARY};
                    background: transparent;
                    border: none;
                    font-size: 9px;
                    font-weight: 700;
                    letter-spacing: 2px;
                    padding: 4px 8px;
                }}
                QPushButton:hover {{
                    color: {Colors.PRIMARY_FIXED};
                }}
            """)
        else:
            self.wireless_btn.setText("🚫 WIRED")
            self.wireless_btn.setStyleSheet(f"""
                QPushButton {{
                    color: {Colors.ERROR};
                    background: transparent;
                    border: none;
                    font-size: 9px;
                    font-weight: 700;
                    letter-spacing: 2px;
                    padding: 4px 8px;
                }}
                QPushButton:hover {{
                    color: {Colors.ERROR_CONT};
                }}
            """)

    def _add_divider(self, layout):
        div = QFrame()
        div.setFrameShape(QFrame.VLine)
        div.setFixedWidth(1)
        div.setFixedHeight(16)
        div.setStyleSheet(f"color: {Colors.OUTLINE_VAR};")
        layout.addWidget(div)

# ─────────────────────────────────────────────
#  SENSOR METRIC CARD
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  LATENCY SPARKLINE CARD
# ─────────────────────────────────────────────
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
        self.sparkline.setFixedSize(60, 32)
        layout.addWidget(self.sparkline, 0, Qt.AlignVCenter)

    def update_value(self, latency):
        self.history.append(latency)
        if len(self.history) > 15:
            self.history.pop(0)
        self.val_lbl.setText(f"{latency} ms")
        self.sparkline.history = self.history
        self.sparkline.update()


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


# ─────────────────────────────────────────────
#  SYSTEM LOGS PANEL
# ─────────────────────────────────────────────
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


class SystemLogsPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

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

        self.logs = [
            ("14:22:04.12", "INFO",   Colors.PRIMARY,          "Object detected in safety zone A-4. Re-calculating path trajectory.", 1.0),
            ("14:22:03.45", "ACTION", Colors.TERTIARY,          "Color identified: #33F4A1. Sorting action completed on sorter 02.", 1.0),
            ("14:21:58.88", "INFO",   Colors.PRIMARY,          "Calibration synchronized with auxiliary sensor hub.", 0.9),
            ("14:21:55.30", "INFO",   Colors.PRIMARY,          "Package 4402 successfully routed to Outbound Terminal.", 0.7),
            ("14:21:42.11", "INFO",   Colors.PRIMARY,          "System initialization sequence finalized. Handshake complete.", 0.5),
        ]
        self._render_logs()

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
        export_btn = QPushButton("↗  EXPORT SESSION DATA")
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: rgba(93,216,226,0.6);
                font-size: 9px;
                letter-spacing: 2px;
                border: none;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                color: {Colors.PRIMARY};
            }}
        """)
        footer_layout.addWidget(export_btn, 0, Qt.AlignCenter)
        layout.addWidget(footer)

        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self._add_random_log)
        self.log_timer.start(3000)
        self.scroll_widget = scroll_widget

    def _render_logs(self):
        while self.log_layout.count():
            child = self.log_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        for ts, tag, color, msg, op in self.logs:
            entry = LogEntry(ts, tag, color, msg, op)
            self.log_layout.addWidget(entry)

    def _add_random_log(self):
        msgs = [
            ("ACTION", Colors.TERTIARY,  "Grip force adjusted: 3.2 N. Object secured."),
            ("INFO",   Colors.PRIMARY,   "Temperature nominal. Cooling fans at 40%."),
            ("INFO",   Colors.PRIMARY,   f"Cycle #{random.randint(1000,9999)} completed in {random.randint(300,800)}ms."),
            ("WARN",   Colors.TERTIARY,  "Proximity sensor threshold approaching limit."),
            ("INFO",   Colors.PRIMARY,   "Vision model confidence: 98.4%. Object classified."),
        ]
        now = datetime.now().strftime("%H:%M:%S.%f")[:11]
        pick = random.choice(msgs)
        self.logs.insert(0, (now, pick[0], pick[1], pick[2], 1.0))
        self.logs = [(ts, t, c, m, max(0.3, o - 0.15)) for ts, t, c, m, o in self.logs]
        if len(self.logs) > 8:
            self.logs.pop()
        self._render_logs()


# ─────────────────────────────────────────────
#  ENVIRONMENT SYNC CARD
# ─────────────────────────────────────────────
class EnvSyncCard(QFrame):
    def __init__(self, image_path=None, base_width=250):
        super().__init__()
        self.setObjectName("card_primary")
        
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.aspect_ratio = 9 / 16
        self.base_width = base_width
        self.base_height = int(base_width / self.aspect_ratio)
        
        self.setFixedSize(self.base_width, self.base_height)
        self.current_pixmap = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.image_container = QWidget()
        self.image_container.setStyleSheet("background: transparent;")
        container_layout = QHBoxLayout(self.image_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        container_layout.addStretch()
        
        self.env_image = QLabel()
        self.env_image.setFixedSize(self.base_width, self.base_height)
        self.env_image.setAlignment(Qt.AlignCenter)
        self.env_image.setStyleSheet("""
            QLabel {
                border-radius: 12px;
                background-color: #0a1a1c;
            }
        """)
        
        container_layout.addWidget(self.env_image)
        container_layout.addStretch()
        
        layout.addWidget(self.image_container)

        if image_path:
            self.set_image(image_path)

    def set_image(self, image_path):
        self.current_pixmap = QPixmap(image_path)
        if not self.current_pixmap.isNull():
            self.update_image_display()
        else:
            print(f"Image not found: {image_path}, using default")
            self.create_default_image()

    def create_default_image(self):
        self.env_image.setText("📷\nEnvironment\nSync")
        self.env_image.setStyleSheet("""
            QLabel {
                border-radius: 12px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a1a1c,
                    stop:1 #1a2a2c
                );
                color: #5dd8e2;
                font-size: 14px;
                font-weight: bold;
            }
        """)

    def update_image_display(self):
        if self.current_pixmap and not self.current_pixmap.isNull():
            scaled_pixmap = self.current_pixmap.scaled(
                self.env_image.width(),
                self.env_image.height(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            
            x_offset = max(0, (scaled_pixmap.width() - self.env_image.width()) // 2)
            y_offset = max(0, (scaled_pixmap.height() - self.env_image.height()) // 2)
            
            cropped = scaled_pixmap.copy(
                x_offset, y_offset,
                self.env_image.width(), self.env_image.height()
            )
            
            self.env_image.setPixmap(cropped)

    def set_width(self, width):
        height = int(width / self.aspect_ratio)
        self.setFixedSize(width, height)
        self.env_image.setFixedSize(width, height)
        
        if self.current_pixmap:
            self.update_image_display()


# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────
class KineticArchitectDashboard(QMainWindow):
    def __init__(self, camnum=0):
        super().__init__()
        self.camnum = camnum
        self.setWindowTitle("Vision-Based Robotic Arm V1.0")
        self.resize(1280, 800)
        self.setMinimumSize(960, 640)
        self.setStyleSheet(STYLESHEET)
        self.showMaximized()

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = SideNavBar()
        root_layout.addWidget(self.sidebar)

        main_area = QWidget()
        main_area.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.topbar = TopBar()
        main_layout.addWidget(self.topbar)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        self.camera_panel = CameraFeedPanel(self.camnum)
        left_col.addWidget(self.camera_panel, stretch=3)

        sensor_row = QHBoxLayout()
        sensor_row.setSpacing(16)
        self.temp_card    = MetricCard("🌡", "34.2", "°C", "Core Temperature", Colors.TERTIARY)
        self.battery_card = MetricCard("⚡", "88",  "%",  "Energy Reserve",   Colors.PRIMARY, border_bottom=True)
        self.latency_card = LatencyCard()

        sensor_row.addWidget(self.temp_card)
        sensor_row.addWidget(self.battery_card)
        sensor_row.addWidget(self.latency_card, stretch=2)
        left_col.addLayout(sensor_row)

        content_layout.addLayout(left_col, stretch=3)

        right_col = QVBoxLayout()
        right_col.setSpacing(16)
        self.logs_panel = SystemLogsPanel()
        self.env_card = EnvSyncCard("../images/robot.jpg", base_width=250)
        right_col.addWidget(self.logs_panel, stretch=1)
        right_col.addWidget(self.env_card)

        content_layout.addLayout(right_col)
        content_layout.setStretch(0, 3)
        content_layout.setStretch(1, 1)

        main_layout.addWidget(content, stretch=1)
        root_layout.addWidget(main_area, stretch=1)

        # Connect topbar signals
        self.topbar.mode_changed.connect(self.camera_panel.set_mode)
        self.topbar.wireless_changed.connect(self._on_wireless_changed)
        self.topbar.power_changed.connect(self._on_power_changed)

        self.data_thread = LiveDataThread()
        self.data_thread.data_updated.connect(self._on_data_update)
        self.data_thread.start()

    def _on_data_update(self, data):
        self.camera_panel.update_data(data)
        self.temp_card.update_value(data["temp"])
        self.battery_card.update_value(data["battery"])
        self.latency_card.update_value(data["latency"])
    
    def _on_wireless_changed(self, is_wireless):
        print(f"Wireless mode: {'ON' if is_wireless else 'OFF (WIRED)'}")
    
    def _on_power_changed(self, is_on):
        print(f"Power: {'ON' if is_on else 'OFF'}")
   
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'env_card'):
            new_width = int(self.width() * 0.18)
            new_width = max(150, min(new_width, 300))
            self.env_card.set_width(new_width)

    def closeEvent(self, event):
        self.data_thread.terminate()
        self.camera_panel.release_camera()
        event.accept()

class RenderUI:
    def __init__(self, name="RenderUI", camnum=0):
        self.name = name
        self.camnum = camnum
    def render(self):
        app = QApplication(sys.argv)
        app.setApplicationName(self.name)

        palette = QPalette()
        palette.setColor(QPalette.Window,          QColor(Colors.SURFACE))
        palette.setColor(QPalette.WindowText,      QColor(Colors.ON_SURFACE))
        palette.setColor(QPalette.Base,            QColor(Colors.SURFACE_CONT))
        palette.setColor(QPalette.AlternateBase,   QColor(Colors.SURFACE_HIGH))
        palette.setColor(QPalette.Text,            QColor(Colors.ON_SURFACE))
        palette.setColor(QPalette.Button,          QColor(Colors.SURFACE_HIGH))
        palette.setColor(QPalette.ButtonText,      QColor(Colors.ON_SURFACE))
        palette.setColor(QPalette.Highlight,       QColor(Colors.PRIMARY))
        palette.setColor(QPalette.HighlightedText, QColor(Colors.ON_PRIMARY))
        app.setPalette(palette)

        window = KineticArchitectDashboard(self.camnum)
        window.show()
        sys.exit(app.exec_())


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    ui = RenderUI()
    ui.render()
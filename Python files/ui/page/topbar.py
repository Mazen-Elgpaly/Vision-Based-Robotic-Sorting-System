# ─────────────────────────────────────────────
#  TOP BAR
# ─────────────────────────────────────────────
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from ui.module.toggleSwitch import AnimatedToggle
from ui.module.toggleMode import AnimatedModeToggle
from ui.style.colors import Colors
from ui.vision.camDetect import CameraFeedPanel
from ui.utility.logger import logger

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
            btn.mousePressEvent = lambda e, i=icon: self.button_clicked(i)
            layout.addWidget(btn)
            layout.addSpacing(8)
    def button_clicked(self, icon):
        if icon == "⌨":
            CameraFeedPanel().toggle_freeze()
            logger.add_log("ACTION", "Toggled Camera Freeze ❄️")
        elif icon == "⚙":
            print("Settings clicked")
        elif icon == "?":
            print("Help clicked")
    
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

# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt
from ui.utility.livethread import LiveDataThread
from ui.vision.camDetect import CameraFeedPanel
from ui.page.sidebar import SideNavBar
from ui.page.topbar import TopBar
from ui.page.manual import ManualControlPage
from ui.page.telemetry import TelemetryPage
from ui.page.diagnostics import DiagnosticsPage
from ui.page.logs import LogsPage
from ui.module.sensorMatricCard import MetricCard
from ui.utility.logspanel import SystemLogsPanel
from ui.style.colors import Colors
from ui.style.styleSheet import STYLESHEET
from ui.module.latencyCard import LatencyCard
from ui.module.envSyncCard import EnvSyncCard

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
        self.sidebar.navigate.connect(self.switch_page)
        root_layout.addWidget(self.sidebar)

        main_area = QWidget()
        main_area.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack = QStackedWidget()

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        self.page_dashboard = content   # اللي انت عامله بالفعل
        self.page_telemetry = TelemetryPage(CameraFeedPanel(self.camnum))
        self.page_manual = ManualControlPage()
        self.page_diagnostics = DiagnosticsPage()
        self.page_logs = LogsPage()

        self.pages = {
            "Dashboard": self.page_dashboard,
            "Telemetry": self.page_telemetry,
            "Manual": self.page_manual,
            "Diagnostics": self.page_diagnostics,
            "Logs": self.page_logs,
        }
        

        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_telemetry)
        self.stack.addWidget(self.page_manual)
        self.stack.addWidget(self.page_diagnostics)
        self.stack.addWidget(self.page_logs)

        self.stack.setCurrentWidget(self.page_dashboard)

        self.topbar = TopBar()
        main_layout.addWidget(self.topbar)

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
        right_col.addWidget(self.env_card, alignment=Qt.AlignmentFlag.AlignCenter)

        content_layout.addLayout(right_col)
        content_layout.setStretch(0, 3)
        content_layout.setStretch(1, 1)

        main_layout.addWidget(self.stack, stretch=1)
        root_layout.addWidget(main_area, stretch=1)

        # Connect topbar signals
        self.topbar.mode_changed.connect(self.camera_panel.set_mode)
        self.topbar.wireless_changed.connect(self._on_wireless_changed)
        self.topbar.power_changed.connect(self._on_power_changed)

        self.data_thread = LiveDataThread()
        self.data_thread.data_updated.connect(self._on_data_update)
        self.data_thread.start()

    def switch_page(self, name):
        self.stack.setCurrentWidget(self.pages[name])

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

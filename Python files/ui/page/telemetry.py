# ─────────────────────────────────────────────
#  Telemetry Page
# ─────────────────────────────────────────────

from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton
import cv2
from ui.style.colors import Colors
from PyQt5.QtCore import Qt
from ui.vision.camDetect import CameraFeedPanel


class TelemetryPage(QWidget):
    def __init__(self, cp: CameraFeedPanel):
        super().__init__()
        self.setObjectName("telemetry")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        label = QLabel("Telemetry Page")
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Calibri", 12))
        label.setStyleSheet(f"color: {Colors.ON_SURFACE}; background: transparent;")
        layout.addWidget(label)
        self.cp = cp 
        self.cp.snapshot_taken.connect(self.handle_image)

    def handle_image(self, img):
        print("وصلت الصورة 🔥")

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        h, w, ch = img.shape
        bytes_per_line = ch * w

        qt_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)

        self.image_label.setPixmap(QPixmap.fromImage(qt_img))
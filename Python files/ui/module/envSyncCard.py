# ─────────────────────────────────────────────
#  ENVIRONMENT SYNC CARD
# ─────────────────────────────────────────────
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

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

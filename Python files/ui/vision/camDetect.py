# ─────────────────────────────────────────────
#  CAMERA FEED PANEL (with shared space for WebView)
# ─────────────────────────────────────────────
import numpy as np
import cv2
import os
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGridLayout, QProgressBar, QSizePolicy

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QGridLayout,
    QSizePolicy, QProgressBar
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView


boxes = []
ignored_points = []

kernel = np.ones((5,5), np.uint8)
class CameraFeedPanel(QFrame):
    frame_updated = pyqtSignal(object)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.capture = None
        self.camera_available = False
        self.mode = "AUTO"
        self.web_view = None
        self.init_ui()
        self.init_camera()
        # Colors
        self.lower_red1 = np.array([0,120,70])
        self.upper_red1 = np.array([10,255,255])
        self.lower_red2 = np.array([170,120,70])
        self.upper_red2 = np.array([180,255,255])

        self.lower_blue = np.array([90,100,50])
        self.upper_blue = np.array([140,255,255])

        self.lower_green = np.array([35,80,50])
        self.upper_green = np.array([85,255,255])

        self.lower_gray = np.array([0,0,45])
        self.upper_gray = np.array([0,0,64])

    def init_ui(self):
        self.setObjectName("card")
        self.setMinimumHeight(300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Split container
        self.split_container = QWidget()
        self.split_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        split_layout = QVBoxLayout(self.split_container)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(0)
        
        # Camera container (will take full space or share with webview)
        self.camera_container = QWidget()
        self.camera_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        camera_layout = QVBoxLayout(self.camera_container)
        camera_layout.setContentsMargins(0, 0, 0, 0)
        camera_layout.setSpacing(0)
        
        # Camera widget
        self.cam_widget = QWidget()
        self.cam_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cam_widget.setStyleSheet("""
            background: #0a1a1c;
            border-radius: 12px;
        """)

        cam_layout = QVBoxLayout(self.cam_widget)
        cam_layout.setContentsMargins(16, 16, 16, 16)

        # Video display label
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(400, 300)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a1a1c,
                    stop:0.5 #0c1e20,
                    stop:1 #070f10
                );
                border-radius: 12px;
            }
        """)
        
        self.video_label.setText("Camera Feed\n(No Signal)")

        # Live badge frame
        self.live_frame = QFrame(self.cam_widget)
        self.live_frame.setStyleSheet("""
            QFrame {
                background: rgba(0,0,0,0.6);
                border-radius: 12px;
                border: 1px solid rgba(93,216,226,0.3);
            }
        """)
        live_layout = QHBoxLayout(self.live_frame)
        live_layout.setContentsMargins(10, 4, 10, 4)
        live_layout.setSpacing(6)

        self.live_dot = QLabel("●")
        self.live_dot.setStyleSheet("color: #5dd8e2; font-size: 8px; background: transparent;")
        live_layout.addWidget(self.live_dot)

        self.live_text = QLabel("LIVE FEED: PRIMARY_OPTICS_01")
        self.live_text.setStyleSheet("color: #e0e0e0; font-size: 9px; letter-spacing: 3px; background: transparent;")
        live_layout.addWidget(self.live_text)
        live_layout.addStretch()

        self.camera_status = QLabel("●")
        self.camera_status.setStyleSheet("color: #5dd8e2; font-size: 8px; background: transparent;")
        live_layout.addWidget(self.camera_status)

        # HUD overlay
        self.hud_frame = QFrame(self.cam_widget)
        self.hud_frame.setStyleSheet("""
            QFrame {
                background: rgba(18,20,22,0.85);
                border-radius: 12px;
                border: 1px solid rgba(62,73,74,0.5);
            }
        """)
        hud_layout = QGridLayout(self.hud_frame)
        hud_layout.setContentsMargins(16, 12, 16, 12)
        hud_layout.setSpacing(8)

        hud_title = QLabel("TELEMETRY HUD")
        hud_title.setStyleSheet("color: #5dd8e2; font-size: 9px; letter-spacing: 3px; font-weight: 600; background: transparent;")
        hud_layout.addWidget(hud_title, 0, 0, 1, 2)

        x_lbl = QLabel("X-AXIS")
        x_lbl.setStyleSheet("color: #a0a0a0; font-size: 8px; letter-spacing: 2px; background: transparent;")
        self.x_val = QLabel("142.08 mm")
        self.x_val.setStyleSheet("color: #e0e0e0; font-size: 16px; font-family: Courier New; font-weight: 700; background: transparent;")
        hud_layout.addWidget(x_lbl, 1, 0)
        hud_layout.addWidget(self.x_val, 2, 0)

        y_lbl = QLabel("Y-AXIS")
        y_lbl.setStyleSheet("color: #a0a0a0; font-size: 8px; letter-spacing: 2px; background: transparent;")
        self.y_val = QLabel("-12.44 mm")
        self.y_val.setStyleSheet("color: #e0e0e0; font-size: 16px; font-family: Courier New; font-weight: 700; background: transparent;")
        hud_layout.addWidget(y_lbl, 1, 1)
        hud_layout.addWidget(self.y_val, 2, 1)

        load_lbl = QLabel("LOAD STATUS")
        load_lbl.setStyleSheet("color: #a0a0a0; font-size: 8px; letter-spacing: 2px; background: transparent;")
        self.load_bar = QProgressBar()
        self.load_bar.setValue(64)
        self.load_bar.setTextVisible(False)
        self.load_bar.setFixedHeight(4)
        self.load_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(62,73,74,0.3);
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: #5dd8e2;
                border-radius: 2px;
            }
        """)
        hud_layout.addWidget(load_lbl, 3, 0, 1, 2)
        hud_layout.addWidget(self.load_bar, 4, 0, 1, 2)

        cam_layout.addWidget(self.video_label)
        
        camera_layout.addWidget(self.cam_widget)
        
        split_layout.addWidget(self.camera_container)
        
        self.main_layout.addWidget(self.split_container)

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._blink)
        self.blink_timer.start(700)
        self._blink_state = True

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_frame)
        self.update_timer.start(50)

    def is_ignored(self, cx, cy):
        for (ix, iy) in ignored_points:
            if abs(cx - ix) < 50 and abs(cy - iy) < 50:
                return True
        return False

    def count_objects(self, mask, color, frame_to_draw):
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
        contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        count = 0

        if color == "red": c = (0,0,255)
        elif color == "blue": c = (255,0,0)
        elif color == "green": c = (0,255,0)
        else: c = (150,150,150) # Gray/Box

        for cnt in contours:
            if cv2.contourArea(cnt) > 1000:
                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = x + w//2, y + h//2

                if self.is_ignored(cx, cy):
                    continue

                count += 1

                # --- [3] أهم تعديل: ميفكرش يدوس لو اللون رصاصي ---
                if color != "box":
                    boxes.append((x, y, w, h, cx, cy))

                # الرسم على الشاشة
                cv2.rectangle(frame_to_draw, (x, y), (x+w, y+h), c, 2)
                cv2.circle(frame_to_draw, (cx, cy), 5, c, -1)
                cv2.putText(frame_to_draw, f"{color} ({cx},{cy})", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, c, 2)

        return count

    def init_camera(self):
        try:
            self.capture = cv2.VideoCapture(self.camera_index)
            if self.capture.isOpened():
                self.camera_available = True
                self.camera_status.setStyleSheet("color: #00ff00; font-size: 8px; background: transparent;")
                self.video_label.setText("")
                print(f"Camera {self.camera_index} initialized successfully")
            else:
                self.camera_available = False
                self.camera_status.setStyleSheet("color: #ff4444; font-size: 8px; background: transparent;")
                self.video_label.setText("Camera Not Available\nCheck Connection")
                print(f"Failed to open camera {self.camera_index}")
        except Exception as e:
            self.camera_available = False
            self.camera_status.setStyleSheet("color: #ff4444; font-size: 8px; background: transparent;")
            print(f"Camera initialization error: {e}")

    def set_mode(self, mode):
        self.mode = mode
        if mode == "MANUAL":
            self.show_web_view()
        else:
            self.hide_web_view()

    def show_web_view(self):
        if not self.web_view:
            # Create web view container
            self.web_container = QWidget()
            self.web_container.setStyleSheet("""
                QWidget {
                    background: white;
                    border-radius: 12px;
                    margin-top: 8px;
                }
            """)
            web_layout = QVBoxLayout(self.web_container)
            web_layout.setContentsMargins(0, 0, 0, 0)
            
            self.web_view = QWebEngineView()
            self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath("ui/page/control.html")))
            web_layout.addWidget(self.web_view)
            
            # Add to split container
            self.split_container.layout().addWidget(self.web_container)
            
            # Set heights - camera takes 70%, webview takes 30%
            self.camera_container.setMinimumHeight(int(self.height() * 0.5))
            self.web_container.setMinimumHeight(int(self.height() * 0.5))

    def hide_web_view(self):
        if self.web_view:
            self.web_container.hide()
            self.split_container.layout().removeWidget(self.web_container)
            self.web_container.deleteLater()
            self.web_view.deleteLater()
            self.web_view = None
            self.web_container = None

    def update_frame(self):
        if not self.camera_available or self.capture is None:
            return

        try:
            ret, frame = self.capture.read()
            if ret:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                # Masks
                red_mask = cv2.inRange(hsv, self.lower_red1, self.upper_red1) + \
                           cv2.inRange(hsv, self.lower_red2, self.upper_red2)

                blue_mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
                green_mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
                gray_mask = cv2.inRange(hsv, self.lower_gray, self.upper_gray)

                # IMPORTANT: ما تخزنش النتيجة في frame
                self.count_objects(red_mask, "red", frame)
                self.count_objects(blue_mask, "blue", frame)
                self.count_objects(green_mask, "green", frame)
                self.count_objects(gray_mask, "box", frame)

                # تحويل لـ RGB للعرض
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w

                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

                self.video_label.setPixmap(QPixmap.fromImage(qt_image))
                self.frame_updated.emit(frame)
            else:
                print("Failed to read frame, attempting to reinitialize camera...")
                self.release_camera()
                self.init_camera()
                
        except Exception as e:
            print(f"Error updating frame: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'hud_frame'):
            self.hud_frame.move(self.cam_widget.width() - self.hud_frame.width() - 16, 
                               self.cam_widget.height() - self.hud_frame.height() - 16)
        if hasattr(self, 'live_frame'):
            self.live_frame.move(16, 16)
        
        # Update sizes when in manual mode
        if self.mode == "MANUAL" and hasattr(self, 'web_container'):
            total_height = self.split_container.height()
            self.camera_container.setMinimumHeight(int(total_height * 0.5))
            self.web_container.setMinimumHeight(int(total_height * 0.3))

    def _blink(self):
        self._blink_state = not self._blink_state
        if self.camera_available:
            color = "#5dd8e2" if self._blink_state else "rgba(93,216,226,0.3)"
        else:
            color = "#ff4444" if self._blink_state else "rgba(255,68,68,0.3)"
        self.live_dot.setStyleSheet(f"color: {color}; font-size: 8px; background: transparent;")

    def update_data(self, data):
        self.x_val.setText(f"{data['x_axis']} mm")
        self.y_val.setText(f"{data['y_axis']} mm")
        self.load_bar.setValue(data['load'])

    def switch_camera(self, camera_index):
        self.camera_index = camera_index
        self.release_camera()
        self.init_camera()

    def release_camera(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None
            self.camera_available = False

    def closeEvent(self, event):
        self.release_camera()
        super().closeEvent(event)

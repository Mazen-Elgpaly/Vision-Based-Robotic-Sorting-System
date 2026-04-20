import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QMainWindow
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from ui.page.mainWindow import KineticArchitectDashboard


class SplashScreen(QWidget):
    def __init__(self, camnum=0):
        super().__init__()
        self.camnum = camnum
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        
        self.image_label = QLabel()
        # نصيحة: استعمل QDir أو مسار كامل لو الصورة مظهرتش
        pixmap = QPixmap("../images/splash.png") 
        pixmap = pixmap.scaled(1000, 1000, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        layout.addWidget(self.image_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 2px solid #222; border-radius: 5px; text-align: center; height: 20px; background-color: #eee; color: #333; }
            QProgressBar::chunk { background-color: #05CC58; }
        """)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.adjustSize()
        self.center() 

        self.timer = QTimer()
        self.timer.timeout.connect(self.loading)
        self.timer.start(30)
        self.counter = 0

    def center(self):
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def loading(self):
        self.progress_bar.setValue(self.counter)
        self.progress_bar.setFormat(f"Loading... {self.counter}%")
        if self.counter >= 101:
            self.timer.stop()
            
            # بنفتح الويندوز الرئيسية ونخليها Reference في الـ Splash قبل ما نقفلها
            self.main_win = KineticArchitectDashboard(self.camnum)
            self.main_win.show()
            
            self.close() # قفل الـ Splash
        self.counter += 1
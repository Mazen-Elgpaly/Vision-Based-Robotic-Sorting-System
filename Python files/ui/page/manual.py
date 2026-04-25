# ─────────────────────────────────────────────
#  Manual Control Page
# ─────────────────────────────────────────────

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton
from ui.style.colors import Colors
from PyQt5.QtCore import Qt


class ManualControlPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("manual")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        label = QLabel("Manual Control")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Calibri", 12))
        label.setStyleSheet(f"color: {Colors.ON_SURFACE}; background: transparent;")
        layout.addWidget(label)
        # Here you can add buttons or controls for manual operation
        # pyuic5 -x manual_widget.ui -o manual_widget_ui.py
        # self.ui = Ui_Form()
        # self.designer_widget = QWidget()
        # self.ui.setupUi(self.designer_widget) # بنقول للديزاينر "ارسم نفسك هنا"
        
        # # 6. ضيف الودجت دي للـ Layout الأساسي بتاع الصفحة
        # layout.addWidget(self.designer_widget)
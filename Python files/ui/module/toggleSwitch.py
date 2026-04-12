# ─────────────────────────────────────────────
#  ANIMATED TOGGLE SWITCH
# ─────────────────────────────────────────────

from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtWidgets import QWidget
from ui.style.colors import Colors

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
)
from PyQt5.QtGui import (
    QColor, QPainter, QBrush
)

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

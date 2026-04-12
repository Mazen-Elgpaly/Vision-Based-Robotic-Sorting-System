# ─────────────────────────────────────────────
#  ANIMATED MODE TOGGLE
# ─────────────────────────────────────────────

from ui.style.colors import Colors
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QRect
)
from PyQt5.QtGui import (
    QColor, QFont, QPainter,
    QPen, QBrush
)

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


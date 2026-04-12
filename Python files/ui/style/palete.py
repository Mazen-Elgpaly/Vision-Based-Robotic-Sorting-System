# ─────────────────────────────────────────────
#  DESIGN TOKENS
# ─────────────────────────────────────────────
from PyQt5.QtGui import QPalette, QColor
from ui.style.colors import Colors

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
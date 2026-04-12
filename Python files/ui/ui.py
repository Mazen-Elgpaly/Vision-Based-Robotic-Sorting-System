# ─────────────────────────────────────────────
#  Main UI Renderer
# ─────────────────────────────────────────────
import sys
from PyQt5.QtWidgets import QApplication
from ui.style.palete import palette
from ui.page.mainWindow import KineticArchitectDashboard

class RenderUI:
    def __init__(self, name="RenderUI", camnum=0):
        self.name = name
        self.camnum = camnum
    def render(self):
        app = QApplication(sys.argv)
        app.setApplicationName(self.name)
        app.setPalette(palette)

        window = KineticArchitectDashboard(self.camnum)
        window.show()
        sys.exit(app.exec_())
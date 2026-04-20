# ─────────────────────────────────────────────
#  Main UI Renderer
# ─────────────────────────────────────────────
import sys
from PyQt5.QtWidgets import QApplication
from ui.style.palete import palette
from ui.page.mainWindow import KineticArchitectDashboard
from ui.utility.splash import SplashScreen

class RenderUI:
    def __init__(self, name="RenderUI", camnum=0, splash=True):
        self.name = name
        self.camnum = camnum
        self.splash = splash
        self.app = None
        self.entry_point = None # عشان نحفظ الـ reference هنا

    def render(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(self.name)
        self.app.setPalette(palette)

        if self.splash:
            # بنشغل الـ Splash وهي اللي هتفتح الـ Dashboard لما تخلص
            self.entry_point = SplashScreen(self.camnum)
            self.entry_point.show()
        else:
            # لو مفيش Splash، افتح الـ Dashboard علطول
            self.entry_point = KineticArchitectDashboard(self.camnum)
            self.entry_point.show()

        # السطر ده بيتكتب مرة واحدة بس في آخر الميثود
        sys.exit(self.app.exec_())
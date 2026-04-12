# ─────────────────────────────────────────────
#  LIVE TICKER: simulates real-time data
# ─────────────────────────────────────────────
import random
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import (
    QThread, pyqtSignal
)

class LiveDataThread(QThread):
    data_updated = pyqtSignal(dict)

    def run(self):
        while True:
            data = {
                "x_axis":     round(random.uniform(130, 160), 2),
                "y_axis":     round(random.uniform(-20, 10), 2),
                "load":       random.randint(50, 85),
                "temp":       round(random.uniform(32, 38), 1),
                "battery":    random.randint(80, 95),
                "latency":    random.randint(8, 25),
            }
            self.data_updated.emit(data)
            self.msleep(1200)


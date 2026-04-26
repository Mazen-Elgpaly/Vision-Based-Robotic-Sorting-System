# ─────────────────────────────────────────────
#  LIVE TICKER: simulates real-time data
# ─────────────────────────────────────────────
import random
from PyQt5.QtCore import QThread, pyqtSignal
import psutil

class LiveDataThread(QThread):
    data_updated = pyqtSignal(dict)

    def run(self):
        while True:
            data = {
                "x_axis":     round(random.uniform(130, 160), 2),
                "y_axis":     round(random.uniform(-20, 10), 2),
                "load":       random.randint(50, 85),
                "temp":       round(psutil.cpu_percent(interval=1), 1),
                "battery":    round(psutil.sensors_battery().percent, 1) if psutil.sensors_battery() else None,
                "ram_usage":  round(psutil.virtual_memory().percent, 1),
                "latency":    random.randint(10, 100),
            }
            self.data_updated.emit(data)
            self.msleep(1200)


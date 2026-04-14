from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from ui.style.colors import Colors

class GlobalLogger(QObject):
    log_signal = pyqtSignal(str, object, str)  # kind, color, text
    
    color_map = {
        "INFO": Colors.PRIMARY,
        "ACTION": Colors.TERTIARY,
        "WARN": Colors.TERTIARY,
    }
    def __init__(self):
        super().__init__()
        self.logs = []  # هنا التخزين

    def add_log(self, kind, text):
        color = self.color_map.get(kind, Colors.PRIMARY)
        now = datetime.now().strftime("%H:%M:%S.%f")[:11]

        log_entry = {
            "time": now,
            "kind": kind,
            "color": color,
            "text": text
        }

        self.logs.insert(0, log_entry)

        # limit (اختياري)
        if len(self.logs) > 1000:
            self.logs.pop()

        # ابعت للـ UI
        self.log_signal.emit(kind, color, text)

    def get_logs(self):
        return self.logs

    def clear_logs(self):
        self.logs.clear()

logger = GlobalLogger()
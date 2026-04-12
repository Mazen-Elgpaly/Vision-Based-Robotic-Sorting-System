# ─────────────────────────────────────────────
#  DESIGN TOKENS
# ─────────────────────────────────────────────
from ui.style.colors import Colors

STYLESHEET = f"""
QMainWindow, QWidget#central {{
    background-color: {Colors.SURFACE};
    color: {Colors.ON_SURFACE};
}}

QLabel {{
    color: {Colors.ON_SURFACE};
    background: transparent;
}}

QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: {Colors.SURFACE_LOWEST};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {Colors.PRIMARY_CONT};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QPushButton {{
    background-color: {Colors.PRIMARY};
    color: {Colors.ON_PRIMARY};
    border: none;
    border-radius: 6px;
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 6px 16px;
    text-transform: uppercase;
}}
QPushButton:hover {{
    background-color: {Colors.PRIMARY_FIXED};
}}
QPushButton:pressed {{
    background-color: {Colors.PRIMARY_CONT};
}}

QPushButton#emergency {{
    background-color: {Colors.ERROR_CONT};
    color: {Colors.ERROR};
    border-radius: 10px;
    padding: 10px;
    font-size: 18px;
}}
QPushButton#emergency:hover {{
    background-color: {Colors.TERTIARY_CONT};
}}

QPushButton#nav_btn {{
    background-color: transparent;
    color: rgba(93,216,226,0.4);
    border: none;
    border-radius: 0px;
    font-size: 8px;
    letter-spacing: 2px;
    padding: 12px 4px;
    text-align: center;
}}
QPushButton#nav_btn:hover {{
    background-color: rgba(93,216,226,0.05);
    color: {Colors.PRIMARY};
}}
QPushButton#nav_btn_active {{
    background-color: rgba(93,216,226,0.1);
    color: {Colors.PRIMARY};
    border: none;
    border-right: 2px solid {Colors.PRIMARY};
    border-radius: 0px;
    font-size: 8px;
    letter-spacing: 2px;
    padding: 12px 4px;
    text-align: center;
}}

QFrame#card {{
    background-color: {Colors.SURFACE_HIGH};
    border-radius: 12px;
    border: 1px solid rgba(93,216,226,0.06);
}}

QFrame#card_primary {{
    background-color: rgba(0,123,131,0.15);
    border-radius: 12px;
    border: 1px solid rgba(93,216,226,0.18);
}}

QFrame#sidebar {{
    background-color: {Colors.SURFACE_LOWEST};
    border-right: 1px solid rgba(93,216,226,0.05);
}}

QFrame#topbar {{
    background-color: {Colors.SURFACE};
    border-bottom: 1px solid rgba(93,216,226,0.10);
}}

QProgressBar {{
    background-color: {Colors.SURFACE_HIGHEST};
    border-radius: 2px;
    height: 4px;
    text-align: center;
    border: none;
}}
QProgressBar::chunk {{
    background-color: {Colors.PRIMARY};
    border-radius: 2px;
}}
"""

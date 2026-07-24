import os
from PyQt5.QtCore import QSize, QByteArray, QBuffer, QIODevice
from PyQt5.QtWidgets import QPushButton, QFrame
from src.vector_graphics import VectorGraphics

EPIC_BLUE = "#0078F2"
EPIC_DARK_BG = "#0E0E11"
EPIC_CARD_BG = "#17181C"
EPIC_BORDER = "#2A2D33"
EPIC_TEXT = "#FFFFFF"
EPIC_DIM = "#A0A0A8"
EPIC_SUCCESS = "#4FBF67"
EPIC_WARNING = "#F8B133"
EPIC_ERROR = "#E63946"

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets")).replace("\\", "/")
CHEV_LIGHT = f"{ASSETS_DIR}/chevron_down_light.svg"
CHEV_HOVER = f"{ASSETS_DIR}/chevron_down_hover.svg"

STYLE = f"""
QMainWindow, QWidget {{
    background-color: {EPIC_DARK_BG};
    color: {EPIC_TEXT};
    font-family: 'Segoe UI', 'Arial', sans-serif;
}}

QScrollArea {{
    border: none;
    background-color: {EPIC_DARK_BG};
}}

QScrollBar:vertical {{
    background: {EPIC_CARD_BG};
    width: 10px;
    border: none;
}}

QScrollBar::handle:vertical {{
    background: {EPIC_BORDER};
    border: none;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: #3A3D43;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QGroupBox {{
    border: 1px solid {EPIC_BORDER};
    border-radius: 0px;
    margin-top: 12px;
    padding: 16px;
    background-color: rgba(23, 24, 28, 238);
    font-size: 11px;
    color: {EPIC_DIM};
    letter-spacing: 1px;
    font-weight: 600;
    text-transform: uppercase;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 6px;
    color: {EPIC_TEXT};
}}

QLabel {{
    color: {EPIC_TEXT};
    font-size: 13px;
    background: transparent;
}}

QLineEdit {{
    background-color: {EPIC_DARK_BG};
    border: 1px solid {EPIC_BORDER};
    border-radius: 0px;
    color: {EPIC_TEXT};
    padding: 10px 12px;
    font-size: 14px;
    font-weight: 500;
}}

QLineEdit:hover {{
    border: 1px solid #3A3D43;
}}

QLineEdit:focus {{
    border: 2px solid {EPIC_BLUE};
    background-color: #12131A;
}}

QComboBox {{
    background-color: {EPIC_DARK_BG};
    border: 1px solid {EPIC_BORDER};
    border-radius: 0px;
    color: {EPIC_TEXT};
    padding: 10px 12px;
    font-size: 13px;
    min-width: 120px;
}}

QComboBox:hover {{
    border: 1px solid #3A3D43;
    background-color: #12131A;
}}

QComboBox::drop-down {{
    border: none;
    width: 28px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}}

QComboBox::down-arrow {{
    image: url("{CHEV_LIGHT}");
    width: 12px;
    height: 12px;
}}

QComboBox::down-arrow:hover {{
    image: url("{CHEV_HOVER}");
}}

QComboBox QAbstractItemView {{
    background-color: {EPIC_CARD_BG};
    border: 1px solid {EPIC_BORDER};
    color: {EPIC_TEXT};
    selection-background-color: {EPIC_BLUE};
    selection-color: #FFFFFF;
    outline: none;
    padding: 4px;
}}

QSlider::groove:horizontal {{
    height: 4px;
    background: {EPIC_BORDER};
    border: none;
}}

QSlider::handle:horizontal {{
    background: {EPIC_BLUE};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 0px;
    border: none;
}}

QSlider::handle:horizontal:hover {{
    background: #2D96FF;
}}

QSlider::sub-page:horizontal {{
    background: {EPIC_BLUE};
    border: none;
}}

QTextEdit {{
    background-color: {EPIC_DARK_BG};
    border: 1px solid {EPIC_BORDER};
    border-radius: 0px;
    color: {EPIC_SUCCESS};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 12px;
    line-height: 1.6;
}}

QPushButton {{
    border-radius: 0px;
    padding: 10px 18px;
    font-size: 13px;
    font-family: 'Segoe UI', sans-serif;
    font-weight: 600;
    border: none;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QPushButton:disabled {{
    background-color: {EPIC_BORDER};
    color: {EPIC_DIM};
}}
"""


def lighten_color(hex_color: str, amount: int) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"#{min(255, r + amount):02x}{min(255, g + amount):02x}{min(255, b + amount):02x}"


def darken_color(hex_color: str, amount: int) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"#{max(0, r - amount):02x}{max(0, g - amount):02x}{max(0, b - amount):02x}"


def epic_btn(text: str, color: str = EPIC_BLUE, hover_color: str = None, icon_type: str = None) -> QPushButton:
    if hover_color is None:
        hover_color = lighten_color(color, 20)

    btn = QPushButton(text)

    if icon_type:
        icon = VectorGraphics.create_icon(icon_type, "#FFFFFF", EPIC_DIM, 16)
        btn.setIcon(icon)
        btn.setIconSize(QSize(16, 16))

    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: #FFFFFF;
            border-radius: 0px;
            padding: 10px 18px;
            font-size: 13px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 600;
            border: none;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {darken_color(color, 15)};
        }}
        QPushButton:disabled {{
            background-color: {EPIC_BORDER};
            color: {EPIC_DIM};
        }}
    """)
    return btn


def h_sep() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"background: {EPIC_BORDER}; max-height: 1px; border: none;")
    return line


def pixmap_to_base64_src(pixmap) -> str:
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.WriteOnly)
    pixmap.save(buffer, "PNG")
    b64_str = byte_array.toBase64().data().decode("utf-8")
    return f"data:image/png;base64,{b64_str}"

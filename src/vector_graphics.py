import os
import re
from PyQt5.QtCore import Qt, QByteArray, QSize, QRectF
from PyQt5.QtGui import QPainter, QPixmap, QIcon
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")


class VectorGraphics:
    """
    Utility class for rendering official downloaded Microsoft Fluent SVG vector icons.
    Supports resolution-independent scaling, High DPI device pixel ratios, dynamic color tinting,
    and automatic Normal/Disabled icon state colors.
    """

    @staticmethod
    def get_svg_data(icon_name: str, color_hex: str = "#FFFFFF") -> bytes:
        file_path = os.path.join(ASSETS_DIR, f"{icon_name}.svg")
        if not os.path.exists(file_path):
            file_path = os.path.join(ASSETS_DIR, "rotate.svg")

        with open(file_path, "r", encoding="utf-8") as f:
            svg_content = f.read()

        tinted_svg = re.sub(r'fill="[^"]*"', f'fill="{color_hex}"', svg_content)
        if f'fill="{color_hex}"' not in tinted_svg:
            tinted_svg = re.sub(r'<path ', f'<path fill="{color_hex}" ', tinted_svg)

        return tinted_svg.encode("utf-8")

    @staticmethod
    def create_pixmap(icon_type: str, color_hex: str = "#4FBF67", logical_size: int = 16) -> QPixmap:
        """Renders a downloaded Fluent SVG icon into a crisp QPixmap matching logical size."""
        app = QApplication.instance()
        dpr = app.devicePixelRatio() if app else 1.0

        pixel_size = max(logical_size, int(logical_size * dpr))

        svg_bytes = VectorGraphics.get_svg_data(icon_type, color_hex)
        renderer = QSvgRenderer(QByteArray(svg_bytes))

        pixmap = QPixmap(pixel_size, pixel_size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        renderer.render(painter, QRectF(0.0, 0.0, float(pixel_size), float(pixel_size)))
        painter.end()

        pixmap.setDevicePixelRatio(dpr)
        return pixmap

    @staticmethod
    def create_icon(icon_type: str, normal_color: str = "#FFFFFF", disabled_color: str = "#A0A0A8", logical_size: int = 16) -> QIcon:
        """
        Returns a QIcon with distinct Normal and Disabled state pixmaps.
        Ensures icon color matches text color in both enabled (white) and disabled (gray) states.
        """
        icon = QIcon()
        pix_normal = VectorGraphics.create_pixmap(icon_type, normal_color, logical_size)
        pix_disabled = VectorGraphics.create_pixmap(icon_type, disabled_color, logical_size)

        icon.addPixmap(pix_normal, QIcon.Normal, QIcon.Off)
        icon.addPixmap(pix_normal, QIcon.Normal, QIcon.On)
        icon.addPixmap(pix_disabled, QIcon.Disabled, QIcon.Off)
        icon.addPixmap(pix_disabled, QIcon.Disabled, QIcon.On)
        return icon


class VectorStatusDot(QWidget):
    """
    Custom status indicator widget using downloaded Fluent status SVG icons.
    Icon color matches text color precisely.
    """
    def __init__(self, color_hex: str = "#E63946", text: str = "OFFLINE", parent=None):
        super().__init__(parent)
        self.color_hex = color_hex
        self.text_label = QLabel(text)
        self.icon_label = QLabel()

        self.text_label.setStyleSheet(f"""
            color: {color_hex};
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 1px;
            background: transparent;
            text-transform: uppercase;
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._update_icon(text, color_hex)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)

    def _update_icon(self, text: str, color_hex: str):
        icon_name = "checkmark" if "ONLINE" in text.upper() else "cross"
        pix = VectorGraphics.create_pixmap(icon_name, color_hex, 16)
        self.icon_label.setPixmap(pix)

    def set_status(self, text: str, color_hex: str):
        self.color_hex = color_hex
        self.text_label.setText(text)
        self.text_label.setStyleSheet(f"""
            color: {color_hex};
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 1px;
            background: transparent;
            text-transform: uppercase;
        """)
        self._update_icon(text, color_hex)


class VectorDirectionBadge(QWidget):
    """
    Custom widget displaying downloaded Fluent SVG direction arrows and text label.
    Icon color matches text color.
    """
    def __init__(self, direction: str = "NONE", color_hex: str = "#A0A0A8", parent=None):
        super().__init__(parent)
        self.direction = direction
        self.color_hex = color_hex
        self.icon_label = QLabel()
        self.text_label = QLabel(direction)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        layout.addStretch()
        layout.addWidget(self.text_label)
        layout.addWidget(self.icon_label)

        self.set_direction(direction, color_hex)

    def set_direction(self, direction: str, color_hex: str = "#FFFFFF"):
        self.direction = direction
        self.color_hex = color_hex
        self.text_label.setText(direction)
        self.text_label.setStyleSheet(f"color:{color_hex}; font-size:14px; font-weight:600;")

        if direction.upper() in ["CW", "CLOCKWISE"]:
            pix = VectorGraphics.create_pixmap("cw", color_hex, 16)
            self.icon_label.setPixmap(pix)
            self.icon_label.setVisible(True)
        elif direction.upper() in ["CCW", "COUNTER-CLOCKWISE"]:
            pix = VectorGraphics.create_pixmap("ccw", color_hex, 16)
            self.icon_label.setPixmap(pix)
            self.icon_label.setVisible(True)
        else:
            self.icon_label.setVisible(False)

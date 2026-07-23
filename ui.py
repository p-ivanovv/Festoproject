import os
from datetime import datetime

from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QByteArray, QBuffer, QIODevice, QSize, QSettings,
    QPropertyAnimation, QEasingCurve
)
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox,
    QSlider, QTextEdit, QGroupBox, QScrollArea,
    QFrame, QSizePolicy, QSpacerItem
)

from motor_controller import MotorController
from src import controls
from src.vector_graphics import VectorGraphics, VectorStatusDot, VectorDirectionBadge
from gist_remote import GistRemoteListener, push_status


EPIC_BLUE = "#0078F2"
EPIC_DARK_BG = "#0E0E11"
EPIC_CARD_BG = "#17181C"
EPIC_BORDER = "#2A2D33"
EPIC_TEXT = "#FFFFFF"
EPIC_DIM = "#A0A0A8"
EPIC_SUCCESS = "#4FBF67"
EPIC_WARNING = "#F8B133"
EPIC_ERROR = "#E63946"

CHEV_LIGHT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "src/assets/chevron_down_light.svg")
).replace("\\", "/")

CHEV_HOVER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "src/assets/chevron_down_hover.svg")
).replace("\\", "/")


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


def lighten_color(hex_color, amount):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = min(255, r + amount)
    g = min(255, g + amount)
    b = min(255, b + amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def darken_color(hex_color, amount):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = max(0, r - amount)
    g = max(0, g - amount)
    b = max(0, b - amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def epic_btn(text, color=EPIC_BLUE, hover_color=None, icon_type=None):
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


def h_sep():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(
        f"background: {EPIC_BORDER}; max-height: 1px; border: none;"
    )
    return line


def pixmap_to_base64_src(pixmap):
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.WriteOnly)
    pixmap.save(buffer, "PNG")
    b64_str = byte_array.toBase64().data().decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


class FestoSplashScreen(QWidget):
    """Short, non-blocking startup view displayed before the main window."""

    def __init__(self):
        super().__init__(
            None,
            Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(440, 250)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("splashCard")
        card.setStyleSheet(f"""
            QFrame#splashCard {{
                background-color: rgba(23, 24, 28, 246);
                border: 1px solid {EPIC_BORDER};
                border-radius: 18px;
            }}
        """)
        root.addWidget(card)

        content = QVBoxLayout(card)
        content.setContentsMargins(36, 32, 36, 32)
        content.setSpacing(10)

        accent = QFrame()
        accent.setFixedHeight(4)
        accent.setStyleSheet(
            f"background-color: {EPIC_BLUE}; border-radius: 2px;"
        )
        content.addWidget(accent)
        content.addStretch()

        title = QLabel("FESTO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {EPIC_TEXT}; font-size: 34px; font-weight: 700; "
            "letter-spacing: 6px;"
        )
        content.addWidget(title)

        subtitle = QLabel("MOTOR CONTROL SYSTEM")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            f"color: {EPIC_BLUE}; font-size: 13px; font-weight: 700; "
            "letter-spacing: 2px;"
        )
        content.addWidget(subtitle)

        status = QLabel("Preparing controller interface - Please wait")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet(f"color: {EPIC_DIM}; font-size: 12px;")
        content.addWidget(status)
        content.addStretch()

        self._fade_animation = None

    def fade_in(self):
        self.setWindowOpacity(0.0)
        self.show()
        self._animate_opacity(0.0, 1.0, 260)

    def fade_out(self, on_finished):
        self._animate_opacity(1.0, 0.0, 360, on_finished)

    def _animate_opacity(self, start, end, duration, on_finished=None):
        self._fade_animation = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_animation.setStartValue(start)
        self._fade_animation.setEndValue(end)
        self._fade_animation.setDuration(duration)
        self._fade_animation.setEasingCurve(QEasingCurve.InOutCubic)
        if on_finished is not None:
            self._fade_animation.finished.connect(on_finished)
        self._fade_animation.start()


class RotateWorker(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(float, float, float, float)

    def __init__(self, controller, degrees, direction, speed_rpm):
        super().__init__()
        self.controller = controller
        self.degrees = degrees
        self.direction = direction
        self.speed_rpm = speed_rpm

    def _progress_cb(self, cur_deg, target_deg, elapsed, total):
        self.progress.emit(cur_deg, target_deg, elapsed, total)

    def run(self):
        ok, msg = self.controller.rotate(
            self.degrees,
            self.direction,
            self.speed_rpm,
            progress_callback=self._progress_cb
        )
        self.finished.emit(ok, msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FESTO MOTOR CONTROL")
        self.setMinimumSize(850, 700)

        self.controller = MotorController()
        self.worker = None
        self.remote = None
        self.last_logged_speed = 30
        self.settings = QSettings("Festo", "FestoMotorControl")

        self.setStyleSheet(STYLE)

        self.icon_check_b64 = pixmap_to_base64_src(
            VectorGraphics.create_pixmap("checkmark", EPIC_SUCCESS, 14)
        )
        self.icon_cross_b64 = pixmap_to_base64_src(
            VectorGraphics.create_pixmap("cross", EPIC_ERROR, 14)
        )

        self._build_ui()

        self._log(
            "System initialized successfully.",
            EPIC_SUCCESS,
            icon_b64=self.icon_check_b64
        )

        self._apply_gist_settings(show_log=False)

    def fade_in(self):
        """Makes the completed desktop interface appear smoothly after splash."""
        self.setWindowOpacity(0.0)
        self._fade_animation = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.setDuration(300)
        self._fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._fade_animation.start()

    def closeEvent(self, event):
        self._log(
            "Closing application: Executing safe hardware cleanup...",
            EPIC_WARNING
        )

        self._push_status()
        controls.cleanup()
        if self.remote is not None:
            self.remote.stop()
        event.accept()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        root = QVBoxLayout(container)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(16)

        root.addWidget(self._make_header())
        root.addWidget(h_sep())
        root.addWidget(self._make_gist_settings_box())
        root.addWidget(self._make_connection_box())

        mid = QHBoxLayout()
        mid.setSpacing(16)
        mid.addWidget(self._make_control_box(), 3)
        mid.addWidget(self._make_status_box(), 2)

        root.addLayout(mid)
        root.addWidget(self._make_presets_box())
        root.addWidget(self._make_log_box())
        root.addItem(
            QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    def _make_header(self):
        widget = QWidget()
        row = QHBoxLayout(widget)
        row.setContentsMargins(0, 0, 0, 0)

        left = QVBoxLayout()

        title = QLabel("MOTOR CONTROL SYSTEM")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {EPIC_TEXT};
            letter-spacing: 0px;
            background: transparent;
        """)

        subtitle = QLabel("Festo Controller Interface")
        subtitle.setStyleSheet(f"""
            color: {EPIC_DIM};
            font-size: 13px;
            background: transparent;
            margin-top: 4px;
        """)

        left.addWidget(title)
        left.addWidget(subtitle)

        self.status_dot = VectorStatusDot(EPIC_ERROR, "OFFLINE")

        row.addLayout(left)
        row.addStretch()
        row.addWidget(self.status_dot)

        return widget

    def _make_gist_settings_box(self):
        group_box = QGroupBox("GitHub Gist Connection")
        column = QVBoxLayout(group_box)
        column.setSpacing(10)

        gist_id_row = QHBoxLayout()
        gist_id_label = QLabel("Gist ID:")
        gist_id_label.setFixedWidth(92)

        self.gist_id_input = QLineEdit()
        self.gist_id_input.setPlaceholderText("Enter Gist ID")
        self.gist_id_input.setText(
            self.settings.value("gist_id", "", type=str)
        )
        gist_id_row.addWidget(gist_id_label)
        gist_id_row.addWidget(self.gist_id_input)
        column.addLayout(gist_id_row)

        token_row = QHBoxLayout()
        token_label = QLabel("Gist token:")
        token_label.setFixedWidth(92)

        self.gist_token_input = QLineEdit()
        self.gist_token_input.setPlaceholderText("Enter GitHub token")
        self.gist_token_input.setEchoMode(QLineEdit.Password)
        self.gist_token_input.setText(
            self.settings.value("gist_token", "", type=str)
        )
        token_row.addWidget(token_label)
        token_row.addWidget(self.gist_token_input)
        column.addLayout(token_row)

        action_row = QHBoxLayout()
        self.apply_gist_btn = epic_btn("Apply Gist Settings", EPIC_BLUE)
        self.apply_gist_btn.clicked.connect(self._apply_gist_settings)

        self.gist_status_label = QLabel("Gist connection is not configured.")
        self.gist_status_label.setStyleSheet(
            f"color:{EPIC_WARNING}; font-size:12px;"
        )
        action_row.addWidget(self.apply_gist_btn)
        action_row.addWidget(self.gist_status_label)
        action_row.addStretch()
        column.addLayout(action_row)

        return group_box

    def _apply_gist_settings(self, show_log=True):
        gist_id = self.gist_id_input.text().strip()
        github_token = self.gist_token_input.text().strip()

        if self.remote is not None:
            self.remote.stop()
            self.remote = None

        if not gist_id or not github_token:
            self.settings.remove("gist_id")
            self.settings.remove("gist_token")
            self.settings.sync()
            self.gist_status_label.setText(
                "Enter both Gist ID and token to enable remote control."
            )
            self.gist_status_label.setStyleSheet(
                f"color:{EPIC_WARNING}; font-size:12px;"
            )
            if show_log:
                self._log(
                    "Gist settings are incomplete. Remote control is disabled.",
                    EPIC_WARNING
                )
            return

        self.settings.setValue("gist_id", gist_id)
        self.settings.setValue("gist_token", github_token)
        self.settings.sync()

        self.remote = GistRemoteListener(gist_id, github_token)
        self.remote.command_received.connect(self.on_remote_command)
        self.remote.start()

        self.gist_status_label.setText("Gist remote control is active.")
        self.gist_status_label.setStyleSheet(
            f"color:{EPIC_SUCCESS}; font-size:12px;"
        )
        if show_log:
            self._log("Gist settings applied. Remote listener started.", EPIC_BLUE)
        else:
            self._log("Gist remote listener started.", EPIC_BLUE)
        self._push_status()

    def _make_connection_box(self):
        group_box = QGroupBox("Connection & Hardware Controls")
        row = QHBoxLayout(group_box)
        row.setSpacing(12)

        row.addWidget(QLabel("Port:"))

        self.port_combo = QComboBox()
        self.port_combo.addItems([
            "COM1", "COM2", "COM3", "COM4",
            "COM5", "COM6", "COM7", "COM8"
        ])
        self.port_combo.setCurrentText("COM3")
        self.port_combo.currentTextChanged.connect(self._on_port_change)
        row.addWidget(self.port_combo)

        row.addWidget(QLabel("Baud Rate:"))

        self.baud_combo = QComboBox()
        self.baud_combo.addItems([
            "9600", "19200", "38400", "57600", "115200"
        ])
        self.baud_combo.setCurrentText("9600")
        self.baud_combo.currentTextChanged.connect(self._on_baud_change)
        row.addWidget(self.baud_combo)

        self.connect_btn = epic_btn(
            "Connect & Reset",
            EPIC_BLUE,
            icon_type="connect"
        )
        self.reset_btn = epic_btn(
            "Reset",
            EPIC_WARNING,
            icon_type="reset"
        )
        self.home_btn = epic_btn(
            "Home",
            EPIC_BLUE,
            icon_type="home"
        )
        self.disconnect_btn = epic_btn(
            "Disconnect",
            EPIC_ERROR,
            icon_type="disconnect"
        )

        self.reset_btn.setEnabled(False)
        self.home_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(False)

        self.connect_btn.clicked.connect(self._on_connect)
        self.reset_btn.clicked.connect(self._on_reset_controller)
        self.home_btn.clicked.connect(self._on_home)
        self.disconnect_btn.clicked.connect(self._on_disconnect)

        row.addStretch()
        row.addWidget(self.connect_btn)
        row.addWidget(self.reset_btn)
        row.addWidget(self.home_btn)
        row.addWidget(self.disconnect_btn)

        return group_box

    def _make_control_box(self):
        group_box = QGroupBox("Rotation Control")
        column = QVBoxLayout(group_box)
        column.setSpacing(16)

        degrees_row = QHBoxLayout()

        degrees_label = QLabel("Degrees:")
        degrees_label.setFixedWidth(80)

        self.degrees_input = QLineEdit()
        self.degrees_input.setPlaceholderText("Enter degrees (e.g. 360)")
        self.degrees_input.setText("360")
        self.degrees_input.textChanged.connect(self._on_degrees_change)

        degrees_row.addWidget(degrees_label)
        degrees_row.addWidget(self.degrees_input)

        column.addLayout(degrees_row)

        direction_row = QHBoxLayout()

        direction_label = QLabel("Direction:")
        direction_label.setFixedWidth(80)

        self.dir_combo = QComboBox()
        self.dir_combo.addItems(["Clockwise", "Counter-Clockwise"])
        self.dir_combo.currentTextChanged.connect(self._on_direction_change)

        direction_row.addWidget(direction_label)
        direction_row.addWidget(self.dir_combo)

        column.addLayout(direction_row)
        column.addWidget(h_sep())

        speed_row = QHBoxLayout()

        speed_label = QLabel("Speed (RPM):")
        speed_label.setFixedWidth(100)

        self.speed_value_lbl = QLabel("30 RPM")
        self.speed_value_lbl.setStyleSheet(
            f"color:{EPIC_BLUE}; font-size:14px; font-weight:700;"
        )
        self.speed_value_lbl.setAlignment(Qt.AlignRight)

        speed_row.addWidget(speed_label)
        speed_row.addStretch()
        speed_row.addWidget(self.speed_value_lbl)

        column.addLayout(speed_row)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 1100)
        self.speed_slider.setValue(30)
        self.speed_slider.valueChanged.connect(self._on_speed_visual_change)
        self.speed_slider.sliderReleased.connect(self._on_speed_released)

        column.addWidget(self.speed_slider)
        column.addWidget(h_sep())

        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        self.rotate_btn = epic_btn(
            "Start Rotation",
            EPIC_BLUE,
            icon_type="rotate"
        )
        self.stop_btn = epic_btn(
            "Emergency Stop",
            EPIC_ERROR,
            icon_type="stop"
        )

        self.stop_btn.setEnabled(False)

        self.rotate_btn.clicked.connect(self._on_rotate)
        self.stop_btn.clicked.connect(self._on_stop)

        button_row.addWidget(self.rotate_btn)
        button_row.addWidget(self.stop_btn)

        column.addLayout(button_row)

        return group_box

    def _make_status_box(self):
        group_box = QGroupBox("Motor Hardware Status")
        column = QVBoxLayout(group_box)
        column.setSpacing(16)

        def info_row(label, default_value):
            row = QHBoxLayout()

            title = QLabel(label)
            title.setStyleSheet(f"color:{EPIC_DIM}; font-size:12px;")

            if isinstance(default_value, QWidget):
                value = default_value
            else:
                value = QLabel(str(default_value))
                value.setStyleSheet(
                    f"color:{EPIC_TEXT}; font-size:14px; font-weight:600;"
                )
                value.setAlignment(Qt.AlignRight)

            row.addWidget(title)
            row.addStretch()
            row.addWidget(value)

            column.addLayout(row)
            return value

        self.lbl_state = info_row("State:", "IDLE")
        self.lbl_power = info_row("Power:", "OFF")
        self.lbl_position = info_row("Position:", "0.00°")
        self.lbl_speed = info_row("Speed:", "0 RPM")

        self.vector_dir_badge = VectorDirectionBadge("NONE", EPIC_DIM)
        info_row("Direction:", self.vector_dir_badge)

        self.lbl_revolutions = info_row("Target Rev:", "0.00")

        return group_box

    def _make_presets_box(self):
        group_box = QGroupBox("Quick Presets")
        row = QHBoxLayout(group_box)
        row.setSpacing(8)

        presets = [
            ("90° (0.25 rev)", 90),
            ("180° (0.5 rev)", 180),
            ("360° (1 rev)", 360),
            ("720° (2 rev)", 720),
            ("1800° (5 rev)", 1800),
        ]

        for label, degrees in presets:
            button = QPushButton(label)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {EPIC_CARD_BG};
                    color: {EPIC_TEXT};
                    border: 1px solid {EPIC_BORDER};
                    border-radius: 0px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 600;
                }}

                QPushButton:hover {{
                    background-color: {EPIC_BORDER};
                    border: 1px solid {EPIC_BLUE};
                }}

                QPushButton:pressed {{
                    background-color: {EPIC_BLUE};
                    color: #FFFFFF;
                }}
            """)

            button.clicked.connect(
                lambda checked, d=degrees, text=label: self._preset_click(d, text)
            )
            row.addWidget(button)

        return group_box

    def _make_log_box(self):
        group_box = QGroupBox("System & Hardware Log")
        column = QVBoxLayout(group_box)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)

        column.addWidget(self.log_text)

        return group_box

    def _log(self, message, color=EPIC_SUCCESS, icon_b64=None):
        timestamp = datetime.now().strftime("%H:%M:%S")

        icon_html = ""

        if icon_b64:
            icon_html = (
                f'<img src="{icon_b64}" width="14" height="14" '
                'style="vertical-align:middle; margin-right:4px;"/> '
            )
        elif color == EPIC_SUCCESS:
            icon_html = (
                f'<img src="{self.icon_check_b64}" width="14" height="14" '
                'style="vertical-align:middle; margin-right:4px;"/> '
            )
        elif color == EPIC_ERROR:
            icon_html = (
                f'<img src="{self.icon_cross_b64}" width="14" height="14" '
                'style="vertical-align:middle; margin-right:4px;"/> '
            )

        self.log_text.append(
            f'<div style="margin:2px 0;">'
            f'<span style="color:{EPIC_DIM}; font-weight:600;">'
            f'[{timestamp}]</span> '
            f'{icon_html}'
            f'<span style="color:{color}; font-weight:500;">'
            f'{message}</span>'
            f'</div>'
        )

        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def _push_status(self):
        """Sends the current desktop UI state to status.json in the Gist."""
        status = {
            "speed": self.speed_slider.value(),
            "degrees": self.degrees_input.text(),
            "direction": (
                "CW"
                if self.dir_combo.currentText() == "Clockwise"
                else "CCW"
            ),
            "state": self.lbl_state.text(),
            "power": self.lbl_power.text(),
        }

        push_status(
            status,
            self.gist_id_input.text(),
            self.gist_token_input.text(),
        )

    def _on_port_change(self, port):
        self._log(f"COM port changed to {port}", EPIC_BLUE)

    def _on_baud_change(self, baud):
        self._log(f"Baud rate changed to {baud}", EPIC_BLUE)

    def _on_degrees_change(self, text):
        if text and text.isdigit():
            degrees = float(text)
            revolutions = degrees / 360.0

            self.lbl_revolutions.setText(f"{revolutions:.4f}")
            self._log(
                f"Target set: {degrees}° ({revolutions:.4f} rev)",
                EPIC_WARNING
            )
            self._push_status()

    def _on_direction_change(self, direction):
        direction_short = "CW" if direction == "Clockwise" else "CCW"

        self.vector_dir_badge.set_direction(direction_short, EPIC_BLUE)
        self._log(f"Direction set to {direction_short}", EPIC_WARNING)
        self._push_status()

    def _on_speed_visual_change(self, value):
        color = EPIC_WARNING if value > 30 else EPIC_BLUE

        self.speed_value_lbl.setText(f"{value} RPM")
        self.speed_value_lbl.setStyleSheet(
            f"color:{color}; font-size:14px; font-weight:700;"
        )

        if value != self.last_logged_speed and not self.speed_slider.isSliderDown():
            self._log(
                f"Speed set to {value} RPM",
                EPIC_WARNING if value > 30 else EPIC_BLUE
            )
            self.last_logged_speed = value

    def _on_speed_released(self):
        value = self.speed_slider.value()

        if value != self.last_logged_speed:
            self._log(
                f"Speed configured: {value} RPM",
                EPIC_WARNING if value > 30 else EPIC_BLUE
            )
            self.last_logged_speed = value

        self._push_status()

    def _preset_click(self, degrees, label):
        self.degrees_input.setText(str(degrees))

        revolutions = degrees / 360.0
        self.lbl_revolutions.setText(f"{revolutions:.4f}")

        self._log(f"Preset applied: {label}", EPIC_BLUE)
        self._push_status()

    def _on_connect(self):
        port = self.port_combo.currentText()
        baud = int(self.baud_combo.currentText())

        self._log(
            f"Connecting to {port} at {baud} baud and initializing controls...",
            EPIC_BLUE
        )

        try:
            ok, message = self.controller.connect(port, baud)
        except Exception as error:
            ok, message = False, str(error)

        if ok:
            self._log(f"Connected: {message}", EPIC_SUCCESS)

            self.status_dot.set_status("ONLINE", EPIC_SUCCESS)

            self.connect_btn.setEnabled(False)
            self.reset_btn.setEnabled(True)
            self.home_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(True)

            self.port_combo.setEnabled(False)
            self.baud_combo.setEnabled(False)

            self.lbl_power.setText("ON")
            self.lbl_power.setStyleSheet(
                f"color:{EPIC_SUCCESS}; font-size:14px; font-weight:600;"
            )

            self._update_position_label()
            self._push_status()
        else:
            self._log(f"Connection failed: {message}", EPIC_ERROR)
            self._push_status()

    def _on_reset_controller(self):
        self._log("Triggering manual controller reset...", EPIC_WARNING)

        ok, message = self.controller.reset_controller()

        if ok:
            self._log(f"Reset complete: {message}", EPIC_SUCCESS)
        else:
            self._log(f"Reset failed: {message}", EPIC_ERROR)

        self._push_status()

    def _on_home(self):
        self._log("Starting homing sequence...", EPIC_BLUE)

        ok, message = self.controller.home(True)

        if ok:
            self._log(f"Homing complete: {message}", EPIC_SUCCESS)
            self._update_position_label()
        else:
            self._log(f"Homing failed: {message}", EPIC_ERROR)

        self._push_status()

    def _on_disconnect(self):
        self._log(
            "Disconnecting and executing hardware cleanup...",
            EPIC_BLUE
        )

        self.controller.disconnect()

        self._log(
            "Disconnected successfully. Power OFF.",
            EPIC_WARNING
        )

        self.status_dot.set_status("OFFLINE", EPIC_ERROR)

        self.connect_btn.setEnabled(True)
        self.reset_btn.setEnabled(False)
        self.home_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(False)

        self.port_combo.setEnabled(True)
        self.baud_combo.setEnabled(True)

        self.lbl_state.setText("IDLE")
        self.lbl_power.setText("OFF")
        self.lbl_power.setStyleSheet(
            f"color:{EPIC_ERROR}; font-size:14px; font-weight:600;"
        )

        self.lbl_speed.setText("0 RPM")
        self.vector_dir_badge.set_direction("NONE", EPIC_DIM)

        self._push_status()

    def _on_rotate(self):
        try:
            degrees = float(self.degrees_input.text())
        except ValueError:
            self._log("Invalid degrees value entered", EPIC_ERROR)
            self._push_status()
            return

        if not self.controller.is_connected():
            self._log("Device not connected", EPIC_ERROR)
            self._push_status()
            return

        direction = (
            "CW"
            if self.dir_combo.currentText() == "Clockwise"
            else "CCW"
        )
        speed_rpm = self.speed_slider.value()
        revolutions = degrees / 360.0

        self._log(
            f"Starting rotation: {degrees}° ({revolutions:.4f} rev) "
            f"{direction} at {speed_rpm} RPM",
            EPIC_BLUE
        )

        self.rotate_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.lbl_state.setText("ROTATING (0.0%)")
        self.lbl_state.setStyleSheet(
            f"color:{EPIC_SUCCESS}; font-size:14px; font-weight:600;"
        )

        self.vector_dir_badge.set_direction(direction, EPIC_BLUE)
        self.lbl_speed.setText(f"{speed_rpm} RPM")

        self.worker = RotateWorker(
            self.controller,
            degrees,
            direction,
            speed_rpm
        )

        self.worker.progress.connect(self._on_rotate_progress)
        self.worker.finished.connect(self._on_rotate_finished)
        self.worker.start()

        self._push_status()

    def _on_rotate_progress(
        self,
        current_deg,
        target_deg,
        elapsed_sec,
        total_sec
    ):
        self.lbl_position.setText(f"{current_deg:.2f}°")

        percentage = (
            min(100.0, (elapsed_sec / total_sec) * 100.0)
            if total_sec > 0
            else 100.0
        )

        self.lbl_state.setText(
            f"ROTATING ({percentage:.1f}%) "
            f"[{elapsed_sec:.1f}s / {total_sec:.1f}s]"
        )

        self.lbl_state.setStyleSheet(
            f"color:{EPIC_SUCCESS}; font-size:14px; font-weight:600;"
        )

    def _on_rotate_finished(self, success, message):
        self.rotate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self.lbl_state.setText("IDLE")
        self.lbl_state.setStyleSheet(
            f"color:{EPIC_DIM}; font-size:14px; font-weight:600;"
        )

        self.lbl_speed.setText("0 RPM")

        if success:
            self._log(f"Rotation complete: {message}", EPIC_SUCCESS)
            self._update_position_label()
        else:
            self._log(f"Rotation failed: {message}", EPIC_ERROR)
            self._update_position_label()

        self._push_status()

    def _on_stop(self):
        self._log("Emergency stop activated!", EPIC_ERROR)

        ok, message = self.controller.stop()

        if ok:
            self._log(f"Stop result: {message}", EPIC_WARNING)

            self.lbl_power.setText("OFF")
            self.lbl_power.setStyleSheet(
                f"color:{EPIC_ERROR}; font-size:14px; font-weight:600;"
            )
        else:
            self._log(f"Stop command failed: {message}", EPIC_ERROR)

        self.rotate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self.lbl_state.setText("STOPPED")
        self.lbl_state.setStyleSheet(
            f"color:{EPIC_ERROR}; font-size:14px; font-weight:600;"
        )

        self.lbl_speed.setText("0 RPM")
        self._update_position_label()
        self._push_status()

    def on_remote_command(self, cmd, value):
        self._log(
            f"[REMOTE] Command received: "
            f"{cmd} {value if value is not None else ''}",
            EPIC_BLUE
        )

        try:
            if cmd == "CONNECT":
                self._on_connect()

            elif cmd == "DISCONNECT":
                self._on_disconnect()

            elif cmd == "SET_DEGREES":
                self.degrees_input.setText(str(value))
                self._push_status()

            elif cmd == "SET_DIRECTION":
                direction = (
                    "Clockwise"
                    if str(value).upper() == "CW"
                    else "Counter-Clockwise"
                )
                self.dir_combo.setCurrentText(direction)
                self._push_status()

            elif cmd == "SET_SPEED":
                speed = int(value)
                speed = max(
                    self.speed_slider.minimum(),
                    min(speed, self.speed_slider.maximum())
                )

                self.speed_slider.setValue(speed)
                self.last_logged_speed = speed

                self._log(f"Remote speed set to {speed} RPM", EPIC_BLUE)
                self._push_status()

            elif cmd == "ROTATE":
                self._on_rotate()

            elif cmd == "STOP":
                self._on_stop()

            elif cmd == "HOME":
                self._on_home()

            elif cmd == "RESET":
                self._on_reset_controller()

            else:
                self._log(f"Unknown remote command: {cmd}", EPIC_ERROR)

        except (TypeError, ValueError) as error:
            self._log(
                f"Invalid remote command value for {cmd}: {error}",
                EPIC_ERROR
            )
            self._push_status()

    def _update_position_label(self):
        position_deg, _ = self.controller.get_position()

        if position_deg is not None:
            self.lbl_position.setText(f"{position_deg:.2f}°")

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox,
    QSlider, QTextEdit, QGroupBox, QScrollArea,
    QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from datetime import datetime
from motor_controller import MotorController

# Epic Games цветова палитра
EPIC_BLUE    = "#0078F2"
EPIC_DARK_BG = "#0E0E11"
EPIC_CARD_BG = "#17181C"
EPIC_BORDER  = "#2A2D33"
EPIC_TEXT    = "#FFFFFF"
EPIC_DIM     = "#A0A0A8"
EPIC_SUCCESS = "#4FBF67"
EPIC_WARNING = "#F8B133"
EPIC_ERROR   = "#E63946"

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
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QGroupBox {{
    border: 1px solid {EPIC_BORDER};
    border-radius: 0px;
    margin-top: 12px;
    padding: 16px;
    background-color: {EPIC_CARD_BG};
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
    width: 30px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {EPIC_DIM};
    width: 0px;
    height: 0px;
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
    padding: 12px 24px;
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


def epic_btn(text, color=EPIC_BLUE, hover_color=None):
    if hover_color is None:
        hover_color = lighten_color(color, 20)
    
    btn = QPushButton(text)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: #FFFFFF;
            border-radius: 0px;
            padding: 12px 24px;
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


def lighten_color(hex_color, amount):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = min(255, r + amount)
    g = min(255, g + amount)
    b = min(255, b + amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def darken_color(hex_color, amount):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = max(0, r - amount)
    g = max(0, g - amount)
    b = max(0, b - amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def h_sep():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"background: {EPIC_BORDER}; max-height:1px; border:none;")
    return line


class RotateWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, controller, degrees, direction, speed):
        super().__init__()
        self.controller = controller
        self.degrees    = degrees
        self.direction  = direction
        self.speed      = speed

    def run(self):
        ok, msg = self.controller.rotate(self.degrees, self.direction, self.speed)
        self.finished.emit(ok, msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FESTO MOTOR CONTROL")
        self.setMinimumSize(800, 650)
        self.showMaximized()
        self.controller    = MotorController()
        self.worker        = None
        self.total_degrees = 0
        self.last_logged_speed = 50
        self.setStyleSheet(STYLE)
        self._build_ui()
        self._log("System initialized successfully", EPIC_SUCCESS)

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
        root.addWidget(self._make_connection_box())

        mid = QHBoxLayout()
        mid.setSpacing(16)
        mid.addWidget(self._make_control_box(), 3)
        mid.addWidget(self._make_status_box(), 2)
        root.addLayout(mid)

        root.addWidget(self._make_presets_box())
        root.addWidget(self._make_log_box())
        root.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _make_header(self):
        w   = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)

        left = QVBoxLayout()
        title = QLabel("MOTOR CONTROL")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {EPIC_TEXT};
            letter-spacing: 0px;
            background: transparent;
        """)
        sub = QLabel("Mazno Demo")
        sub.setStyleSheet(f"""
            color: {EPIC_DIM};
            font-size: 13px;
            background: transparent;
            margin-top: 4px;
        """)
        left.addWidget(title)
        left.addWidget(sub)

        self.status_dot = QLabel("● OFFLINE")
        self.status_dot.setStyleSheet(f"""
            color: {EPIC_ERROR};
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 1px;
            background: transparent;
            text-transform: uppercase;
        """)
        self.status_dot.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        row.addLayout(left)
        row.addStretch()
        row.addWidget(self.status_dot)
        return w

    def _make_connection_box(self):
        gb  = QGroupBox("Connection Settings")
        row = QHBoxLayout(gb)
        row.setSpacing(12)

        row.addWidget(QLabel("Port:"))
        self.port_combo = QComboBox()
        self.port_combo.addItems(["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8"])
        self.port_combo.setCurrentText("COM3")
        self.port_combo.currentTextChanged.connect(self._on_port_change)
        row.addWidget(self.port_combo)

        row.addWidget(QLabel("Baud Rate:"))
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600","19200","38400","57600","115200"])
        self.baud_combo.setCurrentText("9600")
        self.baud_combo.currentTextChanged.connect(self._on_baud_change)
        row.addWidget(self.baud_combo)

        self.connect_btn    = epic_btn("Connect",    EPIC_BLUE)
        self.disconnect_btn = epic_btn("Disconnect", EPIC_ERROR)
        self.disconnect_btn.setEnabled(False)

        self.connect_btn.clicked.connect(self._on_connect)
        self.disconnect_btn.clicked.connect(self._on_disconnect)

        row.addStretch()
        row.addWidget(self.connect_btn)
        row.addWidget(self.disconnect_btn)
        return gb

    def _make_control_box(self):
        gb  = QGroupBox("Rotation Control")
        col = QVBoxLayout(gb)
        col.setSpacing(16)

        deg_row = QHBoxLayout()
        deg_lbl = QLabel("Degrees:")
        deg_lbl.setFixedWidth(80)
        self.degrees_input = QLineEdit()
        self.degrees_input.setPlaceholderText("Enter degrees (0-36000)")
        self.degrees_input.setText("360")
        self.degrees_input.textChanged.connect(self._on_degrees_change)
        deg_row.addWidget(deg_lbl)
        deg_row.addWidget(self.degrees_input)
        col.addLayout(deg_row)

        dir_row = QHBoxLayout()
        dir_lbl = QLabel("Direction:")
        dir_lbl.setFixedWidth(80)
        self.dir_combo = QComboBox()
        self.dir_combo.addItems(["Clockwise", "Counter-Clockwise"])
        self.dir_combo.currentTextChanged.connect(self._on_direction_change)
        dir_row.addWidget(dir_lbl)
        dir_row.addWidget(self.dir_combo)
        col.addLayout(dir_row)

        col.addWidget(h_sep())

        spd_row = QHBoxLayout()
        spd_lbl = QLabel("Speed:")
        spd_lbl.setFixedWidth(80)
        self.speed_value_lbl = QLabel("50%")
        self.speed_value_lbl.setStyleSheet(f"color:{EPIC_BLUE}; font-size:14px; font-weight:700;")
        self.speed_value_lbl.setAlignment(Qt.AlignRight)
        spd_row.addWidget(spd_lbl)
        spd_row.addStretch()
        spd_row.addWidget(self.speed_value_lbl)
        col.addLayout(spd_row)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        self.speed_slider.valueChanged.connect(self._on_speed_visual_change)
        self.speed_slider.sliderReleased.connect(self._on_speed_released)
        col.addWidget(self.speed_slider)

        col.addWidget(h_sep())

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        self.rotate_btn = epic_btn("Start Rotation", EPIC_BLUE)
        self.stop_btn   = epic_btn("Emergency Stop", EPIC_ERROR)
        self.stop_btn.setEnabled(False)
        self.rotate_btn.clicked.connect(self._on_rotate)
        self.stop_btn.clicked.connect(self._on_stop)
        btn_row.addWidget(self.rotate_btn)
        btn_row.addWidget(self.stop_btn)
        col.addLayout(btn_row)

        return gb

    def _make_status_box(self):
        gb  = QGroupBox("Motor Status")
        col = QVBoxLayout(gb)
        col.setSpacing(16)

        def info_row(label, default, color=EPIC_TEXT):
            row = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet(f"color:{EPIC_DIM}; font-size:12px;")
            v = QLabel(default)
            v.setStyleSheet(f"color:{color}; font-size:14px; font-weight:600;")
            v.setAlignment(Qt.AlignRight)
            row.addWidget(l)
            row.addStretch()
            row.addWidget(v)
            col.addLayout(row)
            return v

        self.lbl_state    = info_row("State:",    "IDLE",  EPIC_DIM)
        self.lbl_position = info_row("Position:", "0°",    EPIC_BLUE)
        self.lbl_speed    = info_row("Speed:",    "0%",    EPIC_BLUE)
        self.lbl_dir      = info_row("Direction:","—",     EPIC_TEXT)

        return gb

    def _make_presets_box(self):
        gb  = QGroupBox("Quick Presets")
        row = QHBoxLayout(gb)
        row.setSpacing(8)

        presets = [
            ("90°",      90),
            ("180°",     180),
            ("360°",     360),
            ("720°",     720),
            ("1 Rev",    360),
            ("5 Rev",    1800),
        ]

        for label, deg in presets:
            btn = QPushButton(label)
            btn.setStyleSheet(f"""
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
            btn.clicked.connect(lambda checked, d=deg, l=label: self._preset_click(d, l))
            row.addWidget(btn)

        return gb

    def _make_log_box(self):
        gb  = QGroupBox("System Log")
        col = QVBoxLayout(gb)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        col.addWidget(self.log_text)

        return gb

    def _log(self, message, color=EPIC_SUCCESS):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(
            f'<div style="margin:2px 0;">'
            f'<span style="color:{EPIC_DIM}; font-weight:600;">[{timestamp}]</span> '
            f'<span style="color:{color}; font-weight:500;">{message}</span>'
            f'</div>'
        )
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    # ── Event handlers ───────────────────────────────
    def _on_port_change(self, port):
        self._log(f"COM port changed to {port}", EPIC_BLUE)

    def _on_baud_change(self, baud):
        self._log(f"Baud rate changed to {baud}", EPIC_BLUE)

    def _on_degrees_change(self, text):
        if text and text.isdigit():
            self._log(f"Target degrees set to {text}°", EPIC_WARNING)

    def _on_direction_change(self, direction):
        dir_name = "CW" if direction == "Clockwise" else "CCW"
        self._log(f"Direction changed to {dir_name}", EPIC_WARNING)

    def _on_speed_visual_change(self, value):
        """Визуално update + логване само ако е от клик, не от drag"""
        self.speed_value_lbl.setText(f"{value}%")
        
        # Ако стойността е различна и не се влачи в момента, логвай
        if value != self.last_logged_speed and not self.speed_slider.isSliderDown():
            self._log(f"Speed adjusted to {value}%", EPIC_WARNING)
            self.last_logged_speed = value

    def _on_speed_released(self):
        """Логване само когато се пусне след drag"""
        value = self.speed_slider.value()
        if value != self.last_logged_speed:
            self._log(f"Speed adjusted to {value}%", EPIC_WARNING)
            self.last_logged_speed = value

    def _preset_click(self, degrees, label):
        self.degrees_input.setText(str(degrees))
        self._log(f"Preset applied: {label} ({degrees}°)", EPIC_BLUE)

    def _on_connect(self):
        port = self.port_combo.currentText()
        baud = int(self.baud_combo.currentText())
        
        self._log(f"Connecting to {port} at {baud} baud...", EPIC_BLUE)
        
        try:
            ok, msg = self.controller.connect(port, baud)
        except Exception as e:
            ok, msg = False, str(e)

        if ok:
            self._log(f"✓ {msg}", EPIC_SUCCESS)
            self.status_dot.setText("● ONLINE")
            self.status_dot.setStyleSheet(f"color:{EPIC_SUCCESS}; font-size:14px; font-weight:600; letter-spacing:1px; background:transparent; text-transform:uppercase;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.port_combo.setEnabled(False)
            self.baud_combo.setEnabled(False)
        else:
            self._log(f"✗ Connection failed: {msg}", EPIC_ERROR)

    def _on_disconnect(self):
        self._log("Disconnecting from device...", EPIC_BLUE)
        self.controller.disconnect()
        self._log("✓ Disconnected successfully", EPIC_WARNING)
        
        self.status_dot.setText("● OFFLINE")
        self.status_dot.setStyleSheet(f"color:{EPIC_ERROR}; font-size:14px; font-weight:600; letter-spacing:1px; background:transparent; text-transform:uppercase;")
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.port_combo.setEnabled(True)
        self.baud_combo.setEnabled(True)
        self.lbl_state.setText("IDLE")

    def _on_rotate(self):
        try:
            degrees = int(self.degrees_input.text())
        except ValueError:
            self._log("✗ Invalid degrees value entered", EPIC_ERROR)
            return

        if not self.controller.is_connected():
            self._log("✗ Device not connected", EPIC_ERROR)
            return

        direction = "CW" if self.dir_combo.currentText() == "Clockwise" else "CCW"
        speed     = self.speed_slider.value()

        self._log(f"Starting rotation: {degrees}° {direction} at {speed}%", EPIC_BLUE)

        self.rotate_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.lbl_state.setText("ROTATING")
        self.lbl_state.setStyleSheet(f"color:{EPIC_SUCCESS}; font-size:14px; font-weight:600;")
        self.lbl_dir.setText(direction)
        self.lbl_speed.setText(f"{speed}%")

        self.worker = RotateWorker(self.controller, degrees, direction, speed)
        self.worker.finished.connect(self._on_rotate_finished)
        self.worker.start()

    def _on_rotate_finished(self, success, message):
        self.rotate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.lbl_state.setText("IDLE")
        self.lbl_state.setStyleSheet(f"color:{EPIC_DIM}; font-size:14px; font-weight:600;")

        if success:
            self._log(f"✓ {message}", EPIC_SUCCESS)
            try:
                degrees = int(self.degrees_input.text())
                direction = self.dir_combo.currentText()
                if direction == "Counter-Clockwise":
                    self.total_degrees -= degrees
                else:
                    self.total_degrees += degrees
                
                # Нормализирай в диапазон 0-360°
                display_position = self.total_degrees % 360
                self.lbl_position.setText(f"{display_position}°")
            except:
                pass
        else:
            self._log(f"✗ Rotation failed: {message}", EPIC_ERROR)

    def _on_stop(self):
        self._log("Emergency stop activated!", EPIC_ERROR)
        ok, msg = self.controller.stop()
        if ok:
            self._log(f"✓ {msg}", EPIC_WARNING)
        else:
            self._log(f"✗ Stop command failed: {msg}", EPIC_ERROR)

        self.rotate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.lbl_state.setText("STOPPED")
        self.lbl_state.setStyleSheet(f"color:{EPIC_ERROR}; font-size:14px; font-weight:600;")
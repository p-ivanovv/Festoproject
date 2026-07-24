import os
from datetime import datetime

from PyQt5.QtCore import Qt, QSettings, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox,
    QSlider, QTextEdit, QGroupBox, QScrollArea,
    QFrame, QSizePolicy, QSpacerItem
)

from motor_controller import MotorController
from src import controls
from src.styles import (
    EPIC_BLUE, EPIC_DARK_BG, EPIC_CARD_BG, EPIC_BORDER, EPIC_TEXT,
    EPIC_DIM, EPIC_SUCCESS, EPIC_WARNING, EPIC_ERROR, STYLE,
    epic_btn, h_sep, pixmap_to_base64_src
)
from src.splash import FestoSplashScreen
from src.workers import RotateWorker
from src.vector_graphics import VectorGraphics, VectorStatusDot, VectorDirectionBadge
from gist_remote import GistRemoteListener, push_status


class MainWindow(QMainWindow):
    def __init__(self, no_remote: bool = False):
        super().__init__()

        self.no_remote = no_remote
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

        mode_str = "OFFLINE SIMULATION" if controls.is_offline() else "ONLINE"
        if self.no_remote:
            mode_str += " | NO-REMOTE"
        self._log(f"System initialized ({mode_str}).", EPIC_SUCCESS, icon_b64=self.icon_check_b64)
        self._apply_gist_settings(show_log=False)

    def fade_in(self):
        self.setWindowOpacity(0.0)
        self._fade_animation = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.setDuration(300)
        self._fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._fade_animation.start()

    def closeEvent(self, event):
        self._log("Closing application: Safe hardware cleanup...", EPIC_WARNING)
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
        root.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _make_header(self):
        widget = QWidget()
        row = QHBoxLayout(widget)
        row.setContentsMargins(0, 0, 0, 0)

        left = QVBoxLayout()
        title = QLabel("MOTOR CONTROL SYSTEM")
        title.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {EPIC_TEXT}; background: transparent;")

        subtitle_text = "Festo Controller Interface (Offline Simulation)" if controls.is_offline() else "Festo Controller Interface"
        subtitle = QLabel(subtitle_text)
        subtitle.setStyleSheet(f"color: {EPIC_DIM}; font-size: 13px; background: transparent; margin-top: 4px;")

        left.addWidget(title)
        left.addWidget(subtitle)

        status_text = "SIMULATION" if controls.is_offline() else "ONLINE"
        status_color = EPIC_BLUE if controls.is_offline() else EPIC_SUCCESS
        self.status_dot = VectorStatusDot(status_color, status_text)

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
        self.gist_id_input.setText(self.settings.value("gist_id", "", type=str))
        gist_id_row.addWidget(gist_id_label)
        gist_id_row.addWidget(self.gist_id_input)
        column.addLayout(gist_id_row)

        token_row = QHBoxLayout()
        token_label = QLabel("Gist token:")
        token_label.setFixedWidth(92)

        self.gist_token_input = QLineEdit()
        self.gist_token_input.setPlaceholderText("Enter GitHub token")
        self.gist_token_input.setEchoMode(QLineEdit.Password)
        self.gist_token_input.setText(self.settings.value("gist_token", "", type=str))
        token_row.addWidget(token_label)
        token_row.addWidget(self.gist_token_input)
        column.addLayout(token_row)

        action_row = QHBoxLayout()
        self.apply_gist_btn = epic_btn("Apply Gist Settings", EPIC_BLUE)
        self.apply_gist_btn.clicked.connect(self._apply_gist_settings)

        self.gist_status_label = QLabel("Gist connection is not configured.")
        self.gist_status_label.setStyleSheet(f"color:{EPIC_WARNING}; font-size:12px;")
        action_row.addWidget(self.apply_gist_btn)
        action_row.addWidget(self.gist_status_label)
        action_row.addStretch()
        column.addLayout(action_row)

        return group_box

    def _apply_gist_settings(self, show_log=True):
        if self.no_remote:
            self.gist_status_label.setText("Remote control is disabled (--no-remote mode).")
            self.gist_status_label.setStyleSheet(f"color:{EPIC_DIM}; font-size:12px;")
            self.apply_gist_btn.setEnabled(False)
            self.gist_id_input.setEnabled(False)
            self.gist_token_input.setEnabled(False)
            return

        gist_id = self.gist_id_input.text().strip()
        github_token = self.gist_token_input.text().strip()

        if self.remote is not None:
            self.remote.stop()
            self.remote = None

        if not gist_id or not github_token:
            self.settings.remove("gist_id")
            self.settings.remove("gist_token")
            self.settings.sync()
            self.gist_status_label.setText("Enter both Gist ID and token to enable remote control.")
            self.gist_status_label.setStyleSheet(f"color:{EPIC_WARNING}; font-size:12px;")
            if show_log:
                self._log("Gist settings incomplete. Remote control disabled.", EPIC_WARNING)
            return

        self.settings.setValue("gist_id", gist_id)
        self.settings.setValue("gist_token", github_token)
        self.settings.sync()

        self.remote = GistRemoteListener(gist_id, github_token)
        self.remote.command_received.connect(self.on_remote_command)
        self.remote.start()

        self.gist_status_label.setText("Gist remote control is active.")
        self.gist_status_label.setStyleSheet(f"color:{EPIC_SUCCESS}; font-size:12px;")
        if show_log:
            self._log("Gist settings applied. Remote listener started.", EPIC_BLUE)
        self._push_status()

    def _make_connection_box(self):
        group_box = QGroupBox("Hardware Controls")
        row = QHBoxLayout(group_box)
        row.setSpacing(12)

        self.power_on_btn = epic_btn("Power ON", EPIC_SUCCESS, icon_type="connect")
        self.power_off_btn = epic_btn("Power OFF", EPIC_ERROR, icon_type="stop")
        self.homing_btn = epic_btn("Homing (0°)", EPIC_BLUE, icon_type="home")
        self.reset_btn = epic_btn("Reset Controller", EPIC_WARNING, icon_type="rotate")

        self.power_on_btn.setEnabled(True)
        self.power_off_btn.setEnabled(False)
        self.homing_btn.setEnabled(False)
        self.reset_btn.setEnabled(True)

        self.power_on_btn.clicked.connect(self._on_power_on)
        self.power_off_btn.clicked.connect(self._on_power_off)
        self.homing_btn.clicked.connect(self._on_homing)
        self.reset_btn.clicked.connect(self._on_reset)

        row.addStretch()
        row.addWidget(self.power_on_btn)
        row.addWidget(self.power_off_btn)
        row.addWidget(self.homing_btn)
        row.addWidget(self.reset_btn)

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
        self.speed_value_lbl.setStyleSheet(f"color:{EPIC_BLUE}; font-size:14px; font-weight:700;")
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

        self.rotate_btn = epic_btn("Start Rotation", EPIC_BLUE, icon_type="rotate")
        self.stop_btn = epic_btn("Emergency Stop", EPIC_ERROR, icon_type="stop")

        self.rotate_btn.setEnabled(False)
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
                value.setStyleSheet(f"color:{EPIC_TEXT}; font-size:14px; font-weight:600;")
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

        self.lbl_revolutions = info_row("Target Rev:", "1.0000")

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
            button.clicked.connect(lambda checked, d=degrees, text=label: self._preset_click(d, text))
            row.addWidget(button)

        return group_box

    def _make_log_box(self):
        group_box = QGroupBox("System Log")
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
            icon_html = f'<img src="{icon_b64}" width="14" height="14" style="vertical-align:middle; margin-right:4px;"/> '
        elif color == EPIC_SUCCESS:
            icon_html = f'<img src="{self.icon_check_b64}" width="14" height="14" style="vertical-align:middle; margin-right:4px;"/> '
        elif color == EPIC_ERROR:
            icon_html = f'<img src="{self.icon_cross_b64}" width="14" height="14" style="vertical-align:middle; margin-right:4px;"/> '

        self.log_text.append(
            f'<div style="margin:2px 0;">'
            f'<span style="color:{EPIC_DIM}; font-weight:600;">[{timestamp}]</span> '
            f'{icon_html}'
            f'<span style="color:{color}; font-weight:500;">{message}</span>'
            f'</div>'
        )
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def _push_status(self):
        if self.no_remote:
            return

        status = {
            "speed": self.speed_slider.value(),
            "degrees": self.degrees_input.text(),
            "direction": "CW" if self.dir_combo.currentText() == "Clockwise" else "CCW",
            "state": self.lbl_state.text(),
            "power": self.lbl_power.text(),
        }
        last_cmd_id = self.remote.last_processed_command_id if self.remote is not None else None
        push_status(status, self.gist_id_input.text(), self.gist_token_input.text(), last_command_id=last_cmd_id)

    def _on_degrees_change(self, text):
        if text and text.isdigit():
            degrees = float(text)
            revolutions = degrees / 360.0
            self.lbl_revolutions.setText(f"{revolutions:.4f}")
            self._log(f"Target set: {degrees}° ({revolutions:.4f} rev)", EPIC_WARNING)
            self._push_status()

    def _on_direction_change(self, direction):
        direction_short = "CW" if direction == "Clockwise" else "CCW"
        self.vector_dir_badge.set_direction(direction_short, EPIC_BLUE)
        self._log(f"Direction set to {direction_short}", EPIC_WARNING)
        self._push_status()

    def _on_speed_visual_change(self, value):
        color = EPIC_WARNING if value > 30 else EPIC_BLUE
        self.speed_value_lbl.setText(f"{value} RPM")
        self.speed_value_lbl.setStyleSheet(f"color:{color}; font-size:14px; font-weight:700;")
        if value != self.last_logged_speed and not self.speed_slider.isSliderDown():
            self._log(f"Speed set to {value} RPM", EPIC_WARNING if value > 30 else EPIC_BLUE)
            self.last_logged_speed = value

    def _on_speed_released(self):
        value = self.speed_slider.value()
        if value != self.last_logged_speed:
            self._log(f"Speed configured: {value} RPM", EPIC_WARNING if value > 30 else EPIC_BLUE)
            self.last_logged_speed = value
        self._push_status()

    def _preset_click(self, degrees, label):
        self.degrees_input.setText(str(degrees))
        revolutions = degrees / 360.0
        self.lbl_revolutions.setText(f"{revolutions:.4f}")
        self._log(f"Preset applied: {label}", EPIC_BLUE)
        self._push_status()

    def _on_power_on(self):
        self._log("Enabling motor power...", EPIC_BLUE)
        controls.motor_power(True)
        self.controller._is_powered = True
        self._log("Motor power enabled.", EPIC_SUCCESS)
        self.power_on_btn.setEnabled(False)
        self.power_off_btn.setEnabled(True)
        self.homing_btn.setEnabled(True)
        self.rotate_btn.setEnabled(True)
        self.lbl_power.setText("ON")
        self.lbl_power.setStyleSheet(f"color:{EPIC_SUCCESS}; font-size:14px; font-weight:600;")
        self._push_status()

    def _on_power_off(self):
        self._log("Disabling motor power...", EPIC_WARNING)
        controls.motor_power(False)
        self.controller._is_powered = False
        self._log("Motor power disabled.", EPIC_WARNING)
        self.power_on_btn.setEnabled(True)
        self.power_off_btn.setEnabled(False)
        self.homing_btn.setEnabled(False)
        self.rotate_btn.setEnabled(False)
        self.lbl_power.setText("OFF")
        self.lbl_power.setStyleSheet(f"color:{EPIC_ERROR}; font-size:14px; font-weight:600;")
        self._push_status()

    def _on_homing(self):
        self._log("Starting homing sequence to 0°...", EPIC_BLUE)
        controls.motor_set_homing()
        self.controller._current_position_deg = 0.0
        self._log("Homing to 0° complete.", EPIC_SUCCESS)
        self._update_position_label()
        self._push_status()

    def _on_reset(self):
        self._log("Resetting controller...", EPIC_BLUE)
        controls.controller_reset()
        self._log("Reset complete.", EPIC_SUCCESS)
        self._push_status()

    def _on_rotate(self):
        try:
            degrees = float(self.degrees_input.text())
        except ValueError:
            self._log("Invalid degrees value entered", EPIC_ERROR)
            self._push_status()
            return

        direction = "CW" if self.dir_combo.currentText() == "Clockwise" else "CCW"
        speed_rpm = self.speed_slider.value()
        revolutions = degrees / 360.0

        self._log(f"Starting rotation: {degrees}° ({revolutions:.4f} rev) {direction} at {speed_rpm} RPM", EPIC_BLUE)

        self.rotate_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.homing_btn.setEnabled(False)

        self.lbl_state.setText("ROTATING (0.0%)")
        self.lbl_state.setStyleSheet(f"color:{EPIC_SUCCESS}; font-size:14px; font-weight:600;")
        self.vector_dir_badge.set_direction(direction, EPIC_BLUE)
        self.lbl_speed.setText(f"{speed_rpm} RPM")

        self.worker = RotateWorker(self.controller, degrees, direction, speed_rpm)
        self.worker.progress.connect(self._on_rotate_progress)
        self.worker.finished.connect(self._on_rotate_finished)
        self.worker.start()
        self._push_status()

    def _on_rotate_progress(self, current_deg, target_deg, elapsed_sec, total_sec):
        self.lbl_position.setText(f"{current_deg:.2f}°")
        percentage = min(100.0, (elapsed_sec / total_sec) * 100.0) if total_sec > 0 else 100.0
        self.lbl_state.setText(f"ROTATING ({percentage:.1f}%) [{elapsed_sec:.1f}s / {total_sec:.1f}s]")
        self.lbl_state.setStyleSheet(f"color:{EPIC_SUCCESS}; font-size:14px; font-weight:600;")

    def _on_rotate_finished(self, success, message):
        self.rotate_btn.setEnabled(self.controller.is_powered())
        self.stop_btn.setEnabled(False)
        self.homing_btn.setEnabled(self.controller.is_powered())

        self.lbl_state.setText("IDLE")
        self.lbl_state.setStyleSheet(f"color:{EPIC_DIM}; font-size:14px; font-weight:600;")
        self.lbl_speed.setText("0 RPM")

        if success:
            self._log(f"Rotation complete: {message}", EPIC_SUCCESS)
        else:
            self._log(f"Rotation failed: {message}", EPIC_ERROR)
        self._update_position_label()
        self._push_status()

    def _on_stop(self):
        self._log("Emergency stop activated!", EPIC_ERROR)
        ok, message = self.controller.stop()
        if ok:
            self._log(f"Stop result: {message}", EPIC_WARNING)
            self.power_on_btn.setEnabled(True)
            self.power_off_btn.setEnabled(False)
            self.homing_btn.setEnabled(False)
            self.rotate_btn.setEnabled(False)
            self.lbl_power.setText("OFF")
            self.lbl_power.setStyleSheet(f"color:{EPIC_ERROR}; font-size:14px; font-weight:600;")
        else:
            self._log(f"Stop command failed: {message}", EPIC_ERROR)

        self.stop_btn.setEnabled(False)
        self.lbl_state.setText("STOPPED")
        self.lbl_state.setStyleSheet(f"color:{EPIC_ERROR}; font-size:14px; font-weight:600;")
        self.lbl_speed.setText("0 RPM")
        self._update_position_label()
        self._push_status()

    def on_remote_command(self, cmd, value):
        self._log(f"[REMOTE] Command received: {cmd} {value if value is not None else ''}", EPIC_BLUE)
        try:
            if cmd == "SET_DEGREES":
                self.degrees_input.setText(str(value))
                self._push_status()
            elif cmd == "SET_DIRECTION":
                direction = "Clockwise" if str(value).upper() == "CW" else "Counter-Clockwise"
                self.dir_combo.setCurrentText(direction)
                self._push_status()
            elif cmd == "SET_SPEED":
                speed = int(value)
                speed = max(self.speed_slider.minimum(), min(speed, self.speed_slider.maximum()))
                self.speed_slider.setValue(speed)
                self.last_logged_speed = speed
                self._log(f"Remote speed set to {speed} RPM", EPIC_BLUE)
                self._push_status()
            elif cmd == "ROTATE":
                self._on_rotate()
            elif cmd == "STOP":
                self._on_stop()
            elif cmd in ("HOME", "HOMING"):
                self._on_homing()
            elif cmd == "RESET":
                self._on_reset()
            elif cmd == "POWER_ON":
                self._on_power_on()
            elif cmd == "POWER_OFF":
                self._on_power_off()
            else:
                self._log(f"Unknown remote command: {cmd}", EPIC_ERROR)
        except (TypeError, ValueError) as error:
            self._log(f"Invalid remote command value for {cmd}: {error}", EPIC_ERROR)
            self._push_status()

    def _update_position_label(self):
        position_deg, _ = self.controller.get_position()
        if position_deg is not None:
            self.lbl_position.setText(f"{position_deg:.2f}°")

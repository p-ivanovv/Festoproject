from PyQt5.QtCore import Qt, QSettings, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QGroupBox, QFrame
from src.styles import (
    EPIC_BLUE, EPIC_CARD_BG, EPIC_BORDER, EPIC_TEXT,
    EPIC_DIM, EPIC_SUCCESS, EPIC_WARNING, STYLE, epic_btn, h_sep
)


class SettingsDialog(QDialog):
    settings_saved = pyqtSignal()

    def __init__(self, parent=None, no_remote: bool = False):
        super().__init__(parent)
        self.no_remote = no_remote
        self.settings = QSettings("Festo", "FestoMotorControl")

        self.setWindowTitle("Settings - Festo Motor Control")
        self.setFixedSize(500, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(STYLE)

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        header_row = QHBoxLayout()
        title_label = QLabel("SYSTEM SETTINGS")
        title_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {EPIC_TEXT}; letter-spacing: 1px;")
        header_row.addWidget(title_label)
        header_row.addStretch()
        root.addLayout(header_row)

        root.addWidget(h_sep())

        group_box = QGroupBox("GitHub Gist Remote Control")
        column = QVBoxLayout(group_box)
        column.setSpacing(12)

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
        token_label = QLabel("Gist Token:")
        token_label.setFixedWidth(92)
        self.gist_token_input = QLineEdit()
        self.gist_token_input.setPlaceholderText("Enter GitHub Personal Access Token")
        self.gist_token_input.setEchoMode(QLineEdit.Password)
        self.gist_token_input.setText(self.settings.value("gist_token", "", type=str))
        token_row.addWidget(token_label)
        token_row.addWidget(self.gist_token_input)
        column.addLayout(token_row)

        self.status_label = QLabel()
        self._update_status_label()
        column.addWidget(self.status_label)

        root.addWidget(group_box)
        root.addStretch()

        button_row = QHBoxLayout()
        button_row.addStretch()

        self.save_btn = epic_btn("Save & Apply", EPIC_BLUE)
        self.save_btn.clicked.connect(self._on_save)
        self.close_btn = epic_btn("Close", EPIC_CARD_BG)
        self.close_btn.clicked.connect(self.accept)

        button_row.addWidget(self.save_btn)
        button_row.addWidget(self.close_btn)

        root.addLayout(button_row)

        if self.no_remote:
            self.gist_id_input.setEnabled(False)
            self.gist_token_input.setEnabled(False)
            self.save_btn.setEnabled(False)

    def _update_status_label(self):
        if self.no_remote:
            self.status_label.setText("Remote control is disabled via --no-remote CLI flag.")
            self.status_label.setStyleSheet(f"color:{EPIC_DIM}; font-size:12px;")
            return

        gist_id = self.gist_id_input.text().strip()
        token = self.gist_token_input.text().strip()

        if gist_id and token:
            self.status_label.setText("Gist credentials configured.")
            self.status_label.setStyleSheet(f"color:{EPIC_SUCCESS}; font-size:12px;")
        else:
            self.status_label.setText("Enter both Gist ID and Token to enable remote control.")
            self.status_label.setStyleSheet(f"color:{EPIC_WARNING}; font-size:12px;")

    def _on_save(self):
        if self.no_remote:
            return

        gist_id = self.gist_id_input.text().strip()
        token = self.gist_token_input.text().strip()

        if not gist_id or not token:
            self.settings.remove("gist_id")
            self.settings.remove("gist_token")
        else:
            self.settings.setValue("gist_id", gist_id)
            self.settings.setValue("gist_token", token)

        self.settings.sync()
        self._update_status_label()
        self.settings_saved.emit()
        self.accept()

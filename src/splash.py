from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from src.styles import EPIC_BLUE, EPIC_BORDER, EPIC_TEXT, EPIC_DIM


class FestoSplashScreen(QWidget):
    """Startup view displayed before the main window."""

    def __init__(self):
        super().__init__(None, Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
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
        accent.setStyleSheet(f"background-color: {EPIC_BLUE}; border-radius: 2px;")
        content.addWidget(accent)
        content.addStretch()

        title = QLabel("FESTO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {EPIC_TEXT}; font-size: 34px; font-weight: 700; letter-spacing: 6px;")
        content.addWidget(title)

        subtitle = QLabel("MOTOR CONTROL SYSTEM")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {EPIC_BLUE}; font-size: 13px; font-weight: 700; letter-spacing: 2px;")
        content.addWidget(subtitle)

        status = QLabel("Preparing controller interface...")
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

import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

def setup_hidpi():
    """Configure High DPI scaling parameters prior to QApplication initialization."""
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

def main():
    setup_hidpi()
    app = QApplication(sys.argv)
    app.setApplicationName("Festo Motor Control")
    
    # Delayed import of MainWindow after QApplication setup
    from ui import MainWindow
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
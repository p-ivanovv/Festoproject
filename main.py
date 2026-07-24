import argparse
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication

from src import controls
from ui import FestoSplashScreen, MainWindow


def main():
    parser = argparse.ArgumentParser(description="Festo Motor Control System")
    parser.add_argument("--offline", action="store_true", help="Run in offline simulation mode without CODESYS")
    parser.add_argument("--no-remote", action="store_true", help="Disable GitHub Gist remote control interface")
    args, unknown = parser.parse_known_args()

    controls.set_offline(args.offline)

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Festo Motor Control")

    splash = FestoSplashScreen()
    screen = app.primaryScreen().availableGeometry()
    splash.move(screen.center() - splash.rect().center())
    splash.fade_in()

    def open_main_window():
        window = MainWindow(no_remote=args.no_remote)
        window.showMaximized()
        window.fade_in()

        app.main_window = window
        splash.fade_out(splash.deleteLater)

    QTimer.singleShot(950, open_main_window)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

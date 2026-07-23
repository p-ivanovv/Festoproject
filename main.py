import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from ui import FestoSplashScreen, MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Festo Motor Control")

    splash = FestoSplashScreen()
    screen = app.primaryScreen().availableGeometry()
    splash.move(screen.center() - splash.rect().center())
    splash.fade_in()

    def open_main_window():
        window = MainWindow()
        window.showMaximized()
        window.fade_in()

        # Keep the window alive after this nested callback returns.
        app.main_window = window
        splash.fade_out(splash.deleteLater)

    QTimer.singleShot(950, open_main_window)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Festo Motor Control")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
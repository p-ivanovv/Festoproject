import sys
import unittest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from src.vector_graphics import VectorGraphics, VectorStatusDot, VectorDirectionBadge
from ui import MainWindow

# Initialize HiDPI application for test suite
app = QApplication.instance()
if not app:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)

class TestHiDPIVectorGraphics(unittest.TestCase):

    def test_01_hidpi_attributes(self):
        self.assertTrue(QApplication.testAttribute(Qt.AA_EnableHighDpiScaling))
        self.assertTrue(QApplication.testAttribute(Qt.AA_UseHighDpiPixmaps))

    def test_02_vector_pixmap_generation(self):
        pix_check = VectorGraphics.create_pixmap("checkmark", "#4FBF67", 32)
        self.assertFalse(pix_check.isNull())
        logical_w = pix_check.width() / pix_check.devicePixelRatio()
        self.assertEqual(logical_w, 32)

        pix_cross = VectorGraphics.create_pixmap("cross", "#E63946", 32)
        self.assertFalse(pix_cross.isNull())

        pix_cw = VectorGraphics.create_pixmap("cw", "#0078F2", 32)
        self.assertFalse(pix_cw.isNull())

        pix_ccw = VectorGraphics.create_pixmap("ccw", "#0078F2", 32)
        self.assertFalse(pix_ccw.isNull())

    def test_03_vector_widgets(self):
        dot = VectorStatusDot("#E63946", "OFFLINE")
        self.assertEqual(dot.text_label.text(), "OFFLINE")
        
        dot.set_status("ONLINE", "#4FBF67")
        self.assertEqual(dot.text_label.text(), "ONLINE")

        badge = VectorDirectionBadge("CW", "#0078F2")
        self.assertEqual(badge.direction, "CW")

    def test_04_ui_instantiation(self):
        window = MainWindow()
        self.assertIsNotNone(window)
        self.assertEqual(window.windowTitle(), "FESTO MOTOR CONTROL")
        window.close()

if __name__ == "__main__":
    unittest.main()

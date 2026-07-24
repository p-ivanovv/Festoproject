from PyQt5.QtCore import QThread, pyqtSignal


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

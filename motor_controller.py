import time
from src import controls


class MotorControllerError(Exception):
    pass


class MotorController:
    """High-level interface for Festo motor control."""

    def __init__(self):
        self._connected = True
        self._is_powered = False
        self._current_position_deg = 0.0

    def is_connected(self) -> bool:
        return self._connected

    def connect(self):
        controls.controller_reset()
        controls.motor_power(False)
        controls.motor_position_tracker(True)
        self._connected = True
        self._is_powered = False
        self._current_position_deg = 0.0
        return True, "Controller initialized. Motor power is OFF."

    def reset_controller(self):
        controls.controller_reset()
        return True, "Controller reset complete."

    def power_on(self):
        controls.motor_power(True)
        self._is_powered = True
        return True, "Motor power enabled."

    def power_off(self):
        self._is_powered = False
        controls.motor_power(False)
        return True, "Motor power disabled."

    def is_powered(self) -> bool:
        return self._is_powered

    def home(self):
        controls.motor_set_homing()
        self._current_position_deg = 0.0
        return True, "Homing complete."

    def disconnect(self):
        controls.cleanup()
        self._connected = False
        self._is_powered = False
        return True, "Disconnected and hardware cleaned up."

    def rotate(self, degrees: float, direction: str = "CW", speed_rpm: int = 30, progress_callback=None):
        if not self._is_powered:
            return False, "Safety Alert: Motor power is OFF!"

        try:
            signed_degrees = degrees if direction.upper() in ["CW", "CLOCKWISE"] else -degrees
            revolutions = signed_degrees / 360.0
            start_pos = self._current_position_deg

            controls.motor_speed(speed_rpm)
            controls.motor_revolution(revolutions)
            controls.motor_move()

            duration = max(0.5, abs(revolutions) * 60.0 / max(1, speed_rpm))
            target_interval = 0.5
            steps = max(1, int(duration / target_interval))
            interval = duration / steps

            start_time = time.time()
            for i in range(1, steps + 1):
                if not self._is_powered:
                    return False, "Rotation aborted: Emergency stop activated."
                time.sleep(interval)
                if not self._is_powered:
                    return False, "Rotation aborted: Emergency stop activated."
                elapsed = min(duration, time.time() - start_time)
                ratio = min(1.0, elapsed / duration)
                self._current_position_deg = start_pos + signed_degrees * ratio
                if progress_callback:
                    progress_callback(self._current_position_deg, degrees, elapsed, duration)

            self._current_position_deg = start_pos + signed_degrees
            return True, f"Rotated {degrees}° {direction}"
        except Exception as exc:
            return False, f"Rotation execution failed: {str(exc)}"

    def stop(self):
        return self.power_off()

    def get_position(self):
        return self._current_position_deg, f"Position: {self._current_position_deg:.2f}°"

    def cleanup(self):
        return controls.cleanup()

import time
from src import controls

class MotorControllerError(Exception):
    """Custom exception for motor controller errors"""
    pass


class MotorController:
    """
    High-level controller interface interacting with the low-level motor functions
    defined in `src.controls`. Ensures safe operations, error clearing, speed caps,
    and automatic resource cleanup.

    Position is tracked locally based on rotation parameters —
    no internal controls state is read beyond the spec.
    """

    def __init__(self):
        self._connected = False
        self._current_position_deg = 0.0
        
    def is_connected(self) -> bool:
        return self._connected
    
    def connect(self, port: str = None, baudrate: int = 9600, timeout: float = 1.0):
        """
        Connect to the motor controller and initialize its safety controls:
        1. Perform single controller_reset to clear prior error states.
        2. Enable motor position tracker.
        3. Keep motor power OFF until the operator explicitly enables it.

        ``port`` and ``baudrate`` remain optional for backwards compatibility
        with earlier integrations; the desktop interface no longer exposes
        serial-port settings.
        """
        try:
            # Step 1: Controller reset (Required ONCE before other steps)
            ok_reset, msg_reset = controls.controller_reset()
            if not ok_reset:
                return False, f"Connection failed during reset: {msg_reset}"

            # Step 2: Enable position tracking relative to 0, but do not
            # energize the motor until Power ON is selected in the UI.
            controls.motor_power(False)
            controls.motor_position_tracker(True)

            self._connected = True
            self._current_position_deg = 0.0
            return True, "Controller connected and initialized. Motor power is OFF."
        
        except Exception as exc:
            self._connected = False
            return False, f"Connection error: {str(exc)}"

    def reset_controller(self):
        """Manually trigger controller reset to clear errors."""
        return controls.controller_reset()

    def power_on(self):
        """Supply power to a connected motor after controller initialization."""
        if not self._connected:
            return False, "Not connected. Please connect first."

        controls.motor_power(True)
        return True, "Motor power enabled."

    def power_off(self):
        """Safely cut power to a connected motor."""
        if not self._connected:
            return False, "Not connected. Please connect first."

        controls.motor_power(False)
        return True, "Motor power disabled."

    def is_powered(self) -> bool:
        """Return whether the connected motor is currently powered."""
        return self._connected

    def home(self, enable: bool = True):
        """Execute motor homing sequence to align position to 0."""
        if not self._connected:
            return False, "Not connected. Please connect first."
        ok, msg = controls.motor_set_homing(enable)
        if ok and enable:
            self._current_position_deg = 0.0
        return ok, msg

    def disconnect(self):
        """Disconnect from the motor controller and safely clean up resources."""
        if self._connected:
            controls.cleanup()
            self._connected = False
            self._current_position_deg = 0.0
            return True, "Disconnected and hardware safely cleaned up"
        return True, "Already disconnected"
    
    def rotate(self, degrees: float, direction: str = "CW", speed_rpm: int = 30, progress_callback=None):
        """
        Rotate motor safely by target degrees:
        - Calculates target revolutions: degrees / 360.0
        - Enforces safe speed limits (max 200 RPM, default recommended <= 30 RPM)
        - Tracks position locally based on elapsed time ratio
        - Triggers motion via controls.motor_move()
        """
        if not self._connected:
            return False, "Not connected. Please connect first."

        if not controls.motor_power:
            return False, "Safety Alert: Motor power is OFF!"

        try:
            # Convert degrees to revolutions (1 revolution = 360 degrees)
            signed_degrees = degrees if direction.upper() in ["CW", "CLOCKWISE"] else -degrees
            revolutions = signed_degrees / 360.0
            start_pos = self._current_position_deg

            # Wrap progress callback to track position locally from elapsed ratio
            def _local_progress_cb(cur_deg, target_deg, elapsed, total):
                ratio = min(1.0, elapsed / total) if total > 0 else 1.0
                self._current_position_deg = (start_pos + signed_degrees * ratio) % 360.0
                if progress_callback:
                    progress_callback(self._current_position_deg, target_deg, elapsed, total)

            # Set speed and revolution target in controls
            controls.motor_speed = speed_rpm
            controls.motor_revolution = revolutions

            # Trigger movement with local progress tracking
            ok_move, msg_move = controls.motor_move(progress_callback=_local_progress_cb)

            if ok_move:
                # Set exact final position on success
                self._current_position_deg = (start_pos + signed_degrees) % 360.0

            return ok_move, msg_move
        
        except Exception as exc:
            return False, f"Rotation execution failed: {str(exc)}"
    
    def stop(self):
        """Emergency stop: Cuts motor power immediately."""
        ok, message = self.power_off()
        if not ok:
            return False, message
        return True, "Emergency stop activated. Motor power cut OFF!"
    
    def get_position(self):
        """Get current motor position calculated locally."""
        if not self._connected:
            return None, "Not connected"
        return self._current_position_deg, f"Position: {self._current_position_deg:.2f}°"

    def cleanup(self):
        """Cleanup motor resources on program shutdown."""
        return controls.cleanup()

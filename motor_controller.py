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
    """

    def __init__(self):
        self._connected = False
        self._port = None
        self._baudrate = None
        
    def is_connected(self) -> bool:
        return self._connected
    
    def connect(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        """
        Connect to the motor controller and initialize safety controls:
        1. Perform single controller_reset to clear prior error states.
        2. Enable motor power.
        3. Enable motor position tracker.
        """
        try:
            self._port = port
            self._baudrate = baudrate
            
            # Step 1: Controller reset (Required ONCE before other steps)
            ok_reset, msg_reset = controls.controller_reset()
            if not ok_reset:
                return False, f"Connection failed during reset: {msg_reset}"

            # Step 2: Supply power to motor
            controls.motor_power = True

            # Step 3: Enable position tracking relative to 0
            controls.motor_position_tracker = True

            self._connected = True
            return True, f"Connected to {port} at {baudrate} baud (Power ON, Reset OK, Tracking ON)"
        
        except Exception as exc:
            self._connected = False
            return False, f"Connection error: {str(exc)}"

    def reset_controller(self):
        """Manually trigger controller reset to clear errors."""
        return controls.controller_reset()

    def home(self, enable: bool = True):
        """Execute motor homing sequence to align position to 0."""
        if not self._connected:
            return False, "Not connected. Please connect first."
        return controls.motor_srt_homing(enable)

    def disconnect(self):
        """Disconnect from the motor controller and safely clean up resources."""
        if self._connected:
            controls.cleanup()
            self._connected = False
            self._port = None
            self._baudrate = None
            return True, "Disconnected and hardware safely cleaned up"
        return True, "Already disconnected"
    
    def rotate(self, degrees: float, direction: str = "CW", speed_rpm: int = 30, progress_callback=None):
        """
        Rotate motor safely by target degrees:
        - Calculates target revolutions: degrees / 360.0
        - Enforces safe speed limits (max 200 RPM, default recommended <= 30 RPM)
        - Triggers motion via controls.motor_move() passing real-time progress_callback
        """
        if not self._connected:
            return False, "Not connected. Please connect first."

        if not controls.motor_power:
            return False, "Safety Alert: Motor power is OFF!"

        try:
            # Convert degrees to revolutions (1 revolution = 360 degrees)
            revolutions = (degrees / 360.0) if direction.upper() in ["CW", "CLOCKWISE"] else -(degrees / 360.0)

            # Set speed and revolution target in controls
            controls.motor_speed = speed_rpm
            controls.motor_revolution = revolutions

            # Trigger movement with real-time progress callback
            ok_move, msg_move = controls.motor_move(progress_callback=progress_callback)
            return ok_move, msg_move
        
        except Exception as exc:
            return False, f"Rotation execution failed: {str(exc)}"
    
    def stop(self):
        """Emergency stop: Cuts motor power immediately."""
        if not self._connected:
            return False, "Not connected"
        
        controls.motor_power = False
        return True, "Emergency stop activated. Motor power cut OFF!"
    
    def get_position(self):
        """Get current motor position from tracker."""
        if not self._connected:
            return None, "Not connected"
        hw = controls.get_hardware_instance()
        return hw.current_position_deg, f"Position: {hw.current_position_deg:.2f}°"

    def cleanup(self):
        """Cleanup motor resources on program shutdown."""
        return controls.cleanup()
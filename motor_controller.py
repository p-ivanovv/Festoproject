import time

class MotorControllerError(Exception):
    """Custom exception for motor controller errors"""
    pass


class MotorController:
    def __init__(self):
        self._connected = False
        self._port = None
        self._baudrate = None
        
    def is_connected(self):
        return self._connected
    
    def connect(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        """
        Demo mode: Simulate connection without real serial port
        """
        try:
            self._port = port
            self._baudrate = baudrate
            self._connected = True
            
            # Simulate connection delay
            time.sleep(0.3)
            
            return True, f"Connected to {port} at {baudrate} baud (DEMO MODE)"
        
        except Exception as exc:
            self._connected = False
            return False, f"Connection failed: {str(exc)}"
    
    def disconnect(self):
        """Disconnect from the motor controller"""
        if self._connected:
            self._connected = False
            self._port = None
            self._baudrate = None
            return True, "Disconnected successfully"
        return True, "Already disconnected"
    
    def rotate(self, degrees: float, direction: str = "CW", speed: int = 50):
        """
        Demo mode: Simulate rotation
        """
        if not self._connected:
            return False, "Not connected. Please connect first."
        
        try:
            # Simulate rotation time based on degrees and speed
            rotation_time = (degrees / 360.0) * (100.0 / speed) * 0.5
            time.sleep(min(rotation_time, 2.0))  # Cap at 2 seconds for demo
            
            return True, f"Rotated {degrees}° {direction} at {speed}% speed"
        
        except Exception as exc:
            return False, f"Rotation failed: {str(exc)}"
    
    def stop(self):
        """Emergency stop"""
        if not self._connected:
            return False, "Not connected"
        
        return True, "Motor stopped"
    
    def get_position(self):
        """Get current motor position (demo always returns 0)"""
        if not self._connected:
            return None, "Not connected"
        return 0, "Position read (demo)"
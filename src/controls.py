import sys
import time

class FakeMotorHardware:
    """
    Fake class acting as a placeholder for the real hardware / PLC motor controller interface.
    Implements hardware safety checks, error management, position tracking, homing, and real-time physical motion simulation.
    """
    MAX_RPM_LIMIT = 200
    RECOMMENDED_SAFE_RPM = 30

    def __init__(self):
        self.power = False
        self.reset_done = False
        self.position_tracker = False
        self.target_revolutions = 0.0
        self.speed_rpm = 0
        self.homed = False
        self.current_position_deg = 0.0
        self.is_moving = False

    def controller_reset(self):
        """
        Resets controller to clear errors.
        Should be executed once before performing other motor operations.
        """
        self.reset_done = True
        self.is_moving = False
        print("[FakeMotorHardware] Controller reset executed. Errors cleared.")
        return True, "Controller reset executed. Errors cleared."

    def set_power(self, state: bool):
        """Turns electricity/power to the motor ON (True) or OFF (False)."""
        self.power = bool(state)
        if not self.power:
            self.is_moving = False
        print(f"[FakeMotorHardware] Power state set to: {self.power}")
        return True, f"Motor power set to {self.power}"

    def set_position_tracker(self, state: bool):
        """Enables/disables position tracking relative to origin 0."""
        self.position_tracker = bool(state)
        print(f"[FakeMotorHardware] Position tracking relative to 0 set to: {self.position_tracker}")
        return True, f"Position tracker set to {self.position_tracker}"

    def set_revolution(self, rev: float):
        """Sets target revolutions (REAL). 1 revolution = 360 degrees."""
        self.target_revolutions = float(rev)
        degrees = self.target_revolutions * 360.0
        print(f"[FakeMotorHardware] Target revolutions set to: {self.target_revolutions:.4f} rev ({degrees:.2f}°)")

    def set_speed(self, speed_rpm: int):
        """Sets motor speed in RPM (INT). Safety cap enforced at max 200 RPM."""
        speed_rpm = int(speed_rpm)
        if speed_rpm > self.MAX_RPM_LIMIT:
            print(f"[FakeMotorHardware WARNING] Speed {speed_rpm} RPM exceeds maximum safety limit of {self.MAX_RPM_LIMIT} RPM! Clamped to {self.MAX_RPM_LIMIT} RPM.")
            speed_rpm = self.MAX_RPM_LIMIT
        elif speed_rpm > self.RECOMMENDED_SAFE_RPM:
            print(f"[FakeMotorHardware NOTICE] Speed {speed_rpm} RPM is above recommended threshold of {self.RECOMMENDED_SAFE_RPM} RPM.")
        
        self.speed_rpm = max(0, speed_rpm)
        print(f"[FakeMotorHardware] Motor speed set to: {self.speed_rpm} RPM")

    def motor_srt_homing(self, enable: bool = True):
        """Starts homing sequence to align motor position to zero reference point."""
        if not self.power:
            msg = "Safety Error: Cannot perform homing when motor power is OFF!"
            print(f"[FakeMotorHardware] {msg}")
            return False, msg
        if not self.reset_done:
            msg = "Safety Error: Controller must be reset before homing!"
            print(f"[FakeMotorHardware] {msg}")
            return False, msg

        if enable:
            self.homed = True
            self.current_position_deg = 0.0
            msg = "Homing completed successfully. Motor position set to 0.0°"
            print(f"[FakeMotorHardware] {msg}")
            return True, msg
        return True, "Homing disabled."

    def motor_move(self, progress_callback=None):
        """
        Allows and executes motor rotation based on configured revolutions and speed.
        Simulates exact real-world physical time emitting 20Hz real-time position updates to progress_callback.
        """
        if not self.power:
            msg = "Safety Error: Motor power is OFF! Motion aborted."
            print(f"[FakeMotorHardware] {msg}")
            return False, msg
        if not self.reset_done:
            msg = "Safety Error: Controller has not been reset! Motion aborted."
            print(f"[FakeMotorHardware] {msg}")
            return False, msg
        if self.speed_rpm <= 0:
            msg = "Safety Error: Motor speed must be > 0 RPM! Motion aborted."
            print(f"[FakeMotorHardware] {msg}")
            return False, msg

        self.is_moving = True
        moved_degrees = self.target_revolutions * 360.0
        start_position = self.current_position_deg
        
        # Calculate exact real physical time required in seconds
        physical_time_sec = abs(self.target_revolutions / (self.speed_rpm / 60.0))
        
        # 50ms (20Hz) real-time position update loop
        elapsed = 0.0
        step = 0.05
        while elapsed < physical_time_sec:
            if not self.power:
                self.is_moving = False
                msg = f"Motion aborted by Emergency Stop at {self.current_position_deg:.2f}° after {elapsed:.2f}s!"
                print(f"[FakeMotorHardware] {msg}")
                return False, msg
            
            time.sleep(min(step, physical_time_sec - elapsed))
            elapsed += step

            ratio = min(1.0, elapsed / physical_time_sec)
            current_delta = moved_degrees * ratio

            if self.position_tracker:
                self.current_position_deg = (start_position + current_delta) % 360.0

            if progress_callback:
                progress_callback(self.current_position_deg, moved_degrees, elapsed, physical_time_sec)

        if self.position_tracker:
            self.current_position_deg = (start_position + moved_degrees) % 360.0
            
        self.is_moving = False
        msg = (
            f"Rotated {moved_degrees:.2f}° ({self.target_revolutions:.4f} rev) at {self.speed_rpm} RPM. "
            f"Physical duration: {physical_time_sec:.2f}s (Position: {self.current_position_deg:.2f}°)"
        )
        print(f"[FakeMotorHardware] {msg}")
        return True, msg

    def cleanup(self):
        """Safely stops motor and cuts power upon closing the application."""
        self.is_moving = False
        self.power = False
        msg = "Cleanup complete: Motor stopped and power cut safely."
        print(f"[FakeMotorHardware] {msg}")
        return True, msg


# Global singleton instance of the fake hardware controller
_hardware = FakeMotorHardware()


class _ControlsModuleProxy(sys.modules[__name__].__class__):
    """
    Module proxy allowing attribute access (e.g. controls.motor_power = True)
    to interact directly with the underlying FakeMotorHardware instance.
    """
    @property
    def motor_power(self) -> bool:
        return _hardware.power

    @motor_power.setter
    def motor_power(self, value: bool):
        _hardware.set_power(value)

    @property
    def motor_position_tracker(self) -> bool:
        return _hardware.position_tracker

    @motor_position_tracker.setter
    def motor_position_tracker(self, value: bool):
        _hardware.set_position_tracker(value)

    @property
    def motor_revolution(self) -> float:
        return _hardware.target_revolutions

    @motor_revolution.setter
    def motor_revolution(self, value: float):
        _hardware.set_revolution(value)

    @property
    def motor_speed(self) -> int:
        return _hardware.speed_rpm

    @motor_speed.setter
    def motor_speed(self, value: int):
        _hardware.set_speed(value)


# Explicit functions matching the exact API requirements in the prompt image
def controller_reset():
    """Restarts controller to clear errors (should be run once before other steps)."""
    return _hardware.controller_reset()

def motor_move(progress_callback=None):
    """Allows / triggers motor movement with real-time 20Hz progress callback."""
    return _hardware.motor_move(progress_callback)

def motor_srt_homing(enable: bool = True):
    """Starts motor homing sequence."""
    return _hardware.motor_srt_homing(enable)

def cleanup():
    """Cleans up resources and powers down motor on application exit."""
    return _hardware.cleanup()

# Convenient helper getters for UI/Controller status
def get_hardware_instance() -> FakeMotorHardware:
    return _hardware


# Replace current module with proxy class for property setters/getters support
sys.modules[__name__].__class__ = _ControlsModuleProxy

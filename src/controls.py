import sys
import time

MAX_RPM_LIMIT = 200
RECOMMENDED_SAFE_RPM = 30

# Module-level control variables matching API specification:
# controls.motor_power: BOOL
# controls.motor_position_tracker: BOOL
# controls.motor_revolution: REAL
# controls.motor_speed: INT
motor_power: bool = False
motor_position_tracker: bool = False
motor_revolution: float = 0.0
motor_speed: int = 0

# Internal state variables
reset_done: bool = False
homed: bool = False
current_position_deg: float = 0.0
is_moving: bool = False


def controller_reset():
    """
    Resets controller to clear errors.
    Should be executed once before performing other motor operations.
    """
    global reset_done, is_moving
    reset_done = True
    is_moving = False
    print("[controls] Controller reset executed. Errors cleared.")
    return True, "Controller reset executed. Errors cleared."


def motor_srt_homing(enable: bool = True):
    """
    Starts homing sequence to align motor position to zero reference point.
    """
    global homed, current_position_deg
    if not motor_power:
        msg = "Safety Error: Cannot perform homing when motor power is OFF!"
        print(f"[controls] {msg}")
        return False, msg
    if not reset_done:
        msg = "Safety Error: Controller must be reset before homing!"
        print(f"[controls] {msg}")
        return False, msg

    if enable:
        homed = True
        current_position_deg = 0.0
        msg = "Homing completed successfully. Motor position set to 0.0°"
        print(f"[controls] {msg}")
        return True, msg
    return True, "Homing disabled."


def motor_move(progress_callback=None):
    """
    Allows and executes motor rotation based on configured revolutions and speed.
    Simulates exact real-world physical time emitting 20Hz real-time position updates to progress_callback.
    """
    global is_moving, current_position_deg, motor_speed

    if not motor_power:
        msg = "Safety Error: Motor power is OFF! Motion aborted."
        print(f"[controls] {msg}")
        return False, msg
    if not reset_done:
        msg = "Safety Error: Controller has not been reset! Motion aborted."
        print(f"[controls] {msg}")
        return False, msg

    if motor_speed > MAX_RPM_LIMIT:
        print(f"[controls WARNING] Speed {motor_speed} RPM exceeds maximum safety limit of {MAX_RPM_LIMIT} RPM! Clamped to {MAX_RPM_LIMIT} RPM.")
        motor_speed = MAX_RPM_LIMIT
    elif motor_speed > RECOMMENDED_SAFE_RPM:
        print(f"[controls NOTICE] Speed {motor_speed} RPM is above recommended threshold of {RECOMMENDED_SAFE_RPM} RPM.")

    if motor_speed <= 0:
        msg = "Safety Error: Motor speed must be > 0 RPM! Motion aborted."
        print(f"[controls] {msg}")
        return False, msg

    is_moving = True
    moved_degrees = motor_revolution * 360.0
    start_position = current_position_deg
    
    # Calculate exact real physical time required in seconds
    physical_time_sec = abs(motor_revolution / (motor_speed / 60.0))
    
    # 50ms (20Hz) real-time position update loop
    elapsed = 0.0
    step = 0.05
    while elapsed < physical_time_sec:
        if not motor_power:
            is_moving = False
            msg = f"Motion aborted by Emergency Stop at {current_position_deg:.2f}° after {elapsed:.2f}s!"
            print(f"[controls] {msg}")
            return False, msg
        
        time.sleep(min(step, physical_time_sec - elapsed))
        elapsed += step

        ratio = min(1.0, elapsed / physical_time_sec)
        current_delta = moved_degrees * ratio

        if motor_position_tracker:
            current_position_deg = (start_position + current_delta) % 360.0

        if progress_callback:
            progress_callback(current_position_deg, moved_degrees, elapsed, physical_time_sec)

    if motor_position_tracker:
        current_position_deg = (start_position + moved_degrees) % 360.0
        
    is_moving = False
    msg = (
        f"Rotated {moved_degrees:.2f}° ({motor_revolution:.4f} rev) at {motor_speed} RPM. "
        f"Physical duration: {physical_time_sec:.2f}s (Position: {current_position_deg:.2f}°)"
    )
    print(f"[controls] {msg}")
    return True, msg


def cleanup():
    """
    Safely stops motor and cuts power upon closing the application.
    """
    global is_moving, motor_power
    is_moving = False
    motor_power = False
    msg = "Cleanup complete: Motor stopped and power cut safely."
    print(f"[controls] {msg}")
    return True, msg

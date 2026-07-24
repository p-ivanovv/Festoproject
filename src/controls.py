import os
import time

OFFLINE = os.environ.get("OFFLINE", "0").lower() in ("1", "true", "yes")

try:
    from fthub_codesys.client.codesys_client import CodesysClient
    CODESYS_AVAILABLE = True
except ImportError:
    CODESYS_AVAILABLE = False

codesys_client = None


def set_offline(status: bool = True):
    global OFFLINE
    OFFLINE = status


set_offline_mode = set_offline


def is_offline() -> bool:
    return OFFLINE


def _try_init_codesys():
    global codesys_client
    if not OFFLINE and CODESYS_AVAILABLE and codesys_client is None:
        try:
            print("first")
            codesys_client = CodesysClient(
                codesys_profile='CODESYS V3.5 SP18 Patch 4',
                codesys_ui_mode=False
            )
            print("codesys client executed")
            codesys_client.open_project('codesys_project_table.project')
            time.sleep(1)
            print("Project Opened")
            codesys_client.download()
            time.sleep(1)
            print("Project downloaded")
            codesys_client.run_application()
            time.sleep(1)
            print("App ran")
        except Exception as err:
            print(f"Failed to connect to CODESYS: {err}")
            codesys_client = None


def motor_power(status: bool):
    _try_init_codesys()
    if codesys_client:
        codesys_client.set_variable("GVL.mc_enable", f"{status}")
    print(f"Motor power {status}")


def controller_reset():
    _try_init_codesys()
    if codesys_client:
        codesys_client.set_variable("GVL.mc_reset", "True")
        time.sleep(1)
        codesys_client.set_variable("GVL.mc_reset", "False")
    print("Controller reset")


def motor_position_tracker(status: bool):
    _try_init_codesys()
    if codesys_client:
        codesys_client.set_variable("GVL.mc_speed_enable", f"{status}")
    print(f"Motor tracker {status}")


def motor_move():
    _try_init_codesys()
    if codesys_client:
        codesys_client.set_variable("GVL.mc_move_cmd", "True")
        time.sleep(1)
        codesys_client.set_variable("GVL.mc_move_cmd", "False")
    print("motor movement")


def motor_revolution(degrees: float):
    _try_init_codesys()
    if codesys_client:
        codesys_client.set_variable("GVL.rpm_sp", degrees)
    print(f"Motor set to move {degrees}")


def motor_speed(rpm: int):
    _try_init_codesys()
    if codesys_client:
        codesys_client.set_variable("GVL.velocity_sp", rpm)
    print(f"Motor speed {rpm}")


def motor_set_homing():
    _try_init_codesys()
    if codesys_client:
        codesys_client.set_variable("GVL.home_sp_cmd_activate", "True")
        print("setting new home position")
        codesys_client.set_variable("GVL.home_sp_cmd_activate", "False")
    else:
        print("setting new home position")


def cleanup():
    global codesys_client
    if codesys_client:
        codesys_client.cleanup()
        codesys_client = None
    print("cleanup complete")
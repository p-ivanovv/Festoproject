from fthub_codesys.client.codesys_client import CodesysClient
import time

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


def motor_power(status:bool):
    codesys_client.set_variable("GVL.mc_enable", f"{status}")
    print(f"Motor power {status}")

def controller_reset():
    codesys_client.set_variable("GVL.mc_reset", "True")
    time.sleep(1)
    codesys_client.set_variable("GVL.mc_reset", "False")

def motor_position_tracker(status:bool):
    codesys_client.set_variable("GVL.mc_speed_enable", f"{status}")
    print(f"Motor tracker {status}")

def motor_move():
    codesys_client.set_variable("GVL.mc_move_cmd", "True")
    time.sleep(1)
    codesys_client.set_variable("GVL.mc_move_cmd", "False")
    print("motor movement")

def motor_revolution(degrees:float):
    codesys_client.set_variable("GVL.rpm_sp", degrees)
    print(f"Motor set to move {degrees}")

def motor_speed(rpm:int):
    codesys_client.set_variable("GVL.velocity_sp", rpm)
    print(f"Motor speed {rpm}")

def motor_set_homing():
    codesys_client.set_variable("GVL.home_sp_cmd_activate", "True")
    print("setting new home position")
    codesys_client.set_variable("GVL.home_sp_cmd_activate", "False")

def cleanup():
    codesys_client.cleanup()

# codesys_client.set_variable("GVL.mc_reset", "TRUE")
# time.sleep(1)
# codesys_client.set_variable("GVL.mc_reset", "FALSE")
# codesys_client.set_variable("GVL.mc_enable", "TRUE")
# time.sleep(5)
# codesys_client.set_variable("GVL.home_sp_cmd_activate", "TRUE")
# codesys_client.set_variable("GVL.home_sp_cmd_activate", "FALSE")
# codesys_client.set_variable("GVL.mc_speed_enable", "TRUE")
# codesys_client.set_variable("GVL.velocity_sp", 10)
# codesys_client.set_variable("GVL.rpm_sp", 3.0)
# codesys_client.set_variable("GVL.mc_move_cmd", "TRUE")

# input()
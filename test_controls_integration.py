import sys
import unittest
from src import controls
from motor_controller import MotorController

class TestControlsPackage(unittest.TestCase):

    def setUp(self):
        # Reset state prior to each test
        controls.cleanup()

    def test_01_import_and_properties(self):
        self.assertFalse(controls.motor_power)
        controls.motor_power = True
        self.assertTrue(controls.motor_power)

        controls.motor_position_tracker = True
        self.assertTrue(controls.motor_position_tracker)

        controls.motor_revolution = 2.5
        self.assertAlmostEqual(controls.motor_revolution, 2.5)

        # Test speed limit (capped at 200 RPM)
        controls.motor_speed = 250
        self.assertEqual(controls.motor_speed, 200)

        controls.motor_speed = 30
        self.assertEqual(controls.motor_speed, 30)

    def test_02_reset_and_homing(self):
        ok, msg = controls.controller_reset()
        self.assertTrue(ok)
        
        # Homing without power should fail safely
        controls.motor_power = False
        ok, msg = controls.motor_srt_homing(True)
        self.assertFalse(ok)

        # Power ON -> Homing succeeds
        controls.motor_power = True
        ok, msg = controls.motor_srt_homing(True)
        self.assertTrue(ok)
        self.assertEqual(controls.get_hardware_instance().current_position_deg, 0.0)

    def test_03_motion_safety(self):
        controls.motor_power = False
        ok, msg = controls.motor_move()
        self.assertFalse(ok, "Motion should fail when power is OFF")

        controls.motor_power = True
        # Without reset, motion should fail
        controls.get_hardware_instance().reset_done = False
        ok, msg = controls.motor_move()
        self.assertFalse(ok, "Motion should fail when reset is not completed")

        controls.controller_reset()
        controls.motor_speed = 50
        controls.motor_revolution = 1.0  # 360 degrees
        ok, msg = controls.motor_move()
        self.assertTrue(ok)

    def test_04_motor_controller_wrapper(self):
        mc = MotorController()
        ok, msg = mc.connect("COM3", 9600)
        self.assertTrue(ok)
        self.assertTrue(mc.is_connected())

        # Rotate 180 degrees CW
        ok, msg = mc.rotate(180, "CW", 30)
        self.assertTrue(ok)

        pos, _ = mc.get_position()
        self.assertAlmostEqual(pos, 180.0)

        ok, msg = mc.disconnect()
        self.assertTrue(ok)
        self.assertFalse(mc.is_connected())
        self.assertFalse(controls.motor_power)

if __name__ == "__main__":
    unittest.main()

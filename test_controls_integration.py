import sys
import unittest
from src import controls
from motor_controller import MotorController


class TestControlsPackage(unittest.TestCase):
    """
    All tests access controls exclusively through the spec API:
      controls.motor_power, controls.motor_position_tracker,
      controls.motor_revolution, controls.motor_speed,
      controls.controller_reset(), controls.motor_move(),
      controls.motor_srt_homing(), controls.cleanup()
    """

    def setUp(self):
        # Reset state prior to each test via spec function
        controls.cleanup()

    def test_01_import_and_properties(self):
        """Verify spec variables can be read and written."""
        self.assertFalse(controls.motor_power)
        controls.motor_power = True
        self.assertTrue(controls.motor_power)

        controls.motor_position_tracker = True
        self.assertTrue(controls.motor_position_tracker)

        controls.motor_revolution = 2.5
        self.assertAlmostEqual(controls.motor_revolution, 2.5)

        controls.motor_speed = 30
        self.assertEqual(controls.motor_speed, 30)

    def test_02_reset_and_homing(self):
        """Verify reset and homing through spec functions only."""
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

    def test_03_motion_safety(self):
        """Verify motion safety gates through spec functions only."""
        # Motion should fail when power is OFF
        controls.motor_power = False
        ok, msg = controls.motor_move()
        self.assertFalse(ok, "Motion should fail when power is OFF")

        # After proper setup, motion should succeed
        controls.controller_reset()
        controls.motor_power = True
        controls.motor_speed = 50
        controls.motor_revolution = 1.0  # 360 degrees
        ok, msg = controls.motor_move()
        self.assertTrue(ok)

    def test_04_motor_controller_wrapper(self):
        """Verify MotorController tracks position locally without non-spec access."""
        mc = MotorController()
        ok, msg = mc.connect("COM3", 9600)
        self.assertTrue(ok)
        self.assertTrue(mc.is_connected())

        # Connection prepares the controller but leaves motor power OFF.
        pos, _ = mc.get_position()
        self.assertAlmostEqual(pos, 0.0)
        self.assertFalse(mc.is_powered())

        ok, msg = mc.power_on()
        self.assertTrue(ok)
        self.assertTrue(mc.is_powered())

        # Rotate 180 degrees CW
        ok, msg = mc.rotate(180, "CW", 30)
        self.assertTrue(ok)

        # Position tracked locally by MotorController
        pos, _ = mc.get_position()
        self.assertAlmostEqual(pos, 180.0)

        # Homing returns the tracked position to the zero reference.
        ok, msg = mc.home()
        self.assertTrue(ok)
        pos, _ = mc.get_position()
        self.assertAlmostEqual(pos, 0.0)

        ok, msg = mc.power_off()
        self.assertTrue(ok)
        self.assertFalse(mc.is_powered())

        ok, msg = mc.disconnect()
        self.assertTrue(ok)
        self.assertFalse(mc.is_connected())
        self.assertFalse(controls.motor_power)


if __name__ == "__main__":
    unittest.main()

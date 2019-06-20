from . import common


class TestMachineActive(common.TestMachineCommon):
    """Class to test machine.instance active/inactive functionality."""

    def test_01_toggle_active(self):
        """Make one instance inactive/active."""
        self.mit_1_1.toggle_active()
        self.assertFalse(self.mit_1_1.active)
        self.assertTrue(self.machine_template_1.active)
        self.assertTrue(self.mit_1_2.active)
        self.assertTrue(self.mit_1_3.active)
        self.mit_1_1.toggle_active()
        self.assertTrue(self.mit_1_1.active)
        self.assertTrue(self.machine_template_1.active)
        self.assertTrue(self.mit_1_2.active)
        self.assertTrue(self.mit_1_3.active)

    def test_02_toggle_active(self):
        """Make template inactive/active.

        Case: all related instances are active.
        """
        self.machine_template_1.toggle_active()
        self.assertFalse(self.machine_template_1.active)
        self.assertFalse(self.mit_1_1.active)
        self.assertFalse(self.mit_1_2.active)
        self.assertFalse(self.mit_1_3.active)
        self.machine_template_1.toggle_active()
        self.assertTrue(self.machine_template_1.active)
        self.assertTrue(self.mit_1_1.active)
        self.assertTrue(self.mit_1_2.active)
        self.assertTrue(self.mit_1_3.active)

    def test_03_toggle_active(self):
        """Make template inactive/active.

        Case: some related instances are active, some inactive.
        """
        self.mit_1_1.toggle_active()
        self.machine_template_1.toggle_active()
        self.assertFalse(self.machine_template_1.active)
        self.assertFalse(self.mit_1_1.active)
        self.assertFalse(self.mit_1_2.active)
        self.assertFalse(self.mit_1_3.active)
        self.machine_template_1.toggle_active()
        self.assertTrue(self.machine_template_1.active)
        self.assertTrue(self.mit_1_1.active)
        self.assertTrue(self.mit_1_2.active)
        self.assertTrue(self.mit_1_3.active)

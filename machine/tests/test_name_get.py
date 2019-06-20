from . import common


class TestNameGet(common.TestMachineCommon):
    """Class to test what generate_names outputs for name_get."""

    def test_name_get(self):
        """Sanity checks for name_get."""
        self.assertEqual(self.cpu_xeon.name_get()[0][1], 'Intel Xeon E3113')
        self.assertEqual(self.os_ubuntu_1604.name_get()[0][1], 'Ubuntu 16.04')
        self.assertEqual(
            self.db_postgresql_960.name_get()[0][1], 'PostgreSQL 9.60')

from . import common


class TestMachineValues(common.TestMachineCommon):
    """Class to test various generated machine module values."""

    def test_01_name_get(self):
        """Sanity checks for name_get."""
        self.assertEqual(self.cpu_xeon.name_get()[0][1], 'Intel Xeon E3113')
        self.assertEqual(self.os_ubuntu_1604.name_get()[0][1], 'Ubuntu 16.04')
        self.assertEqual(self.db_postgresql_960.name_get()[0][1], 'PostgreSQL 9.60')

    def test_02_name_get(self):
        """Generate display_name for machine instance.

        Case 1: only name set.
        Case 2: name, domain and IP (not matching).
        Case 3: name and domain (matching).
        Case 4: name, domain and IP (matching).
        Case 5: name and IP.
        """
        # Case 1.
        self.machine_instance_gemini.write({'domain': False, 'ip': False})
        self.assertEqual(
            self.machine_instance_gemini.display_name, self.machine_instance_gemini.name
        )
        # Case 2.
        self.assertEqual(
            self.machine_instance_wood.display_name,
            f'[{self.machine_instance_wood.name}] '
            f'{self.machine_instance_wood.domain}',
        )
        # Case 3.
        self.machine_instance_deco.ip = False
        self.assertEqual(
            self.machine_instance_deco.display_name,
            f'{self.machine_instance_deco.domain}',
        )
        # Case 4.
        self.assertEqual(
            self.machine_instance_readymat.display_name,
            f'{self.machine_instance_readymat.domain}',
        )
        # Case 5.
        self.machine_instance_readymat.domain = False
        self.machine_instance_readymat.invalidate_cache()
        self.assertEqual(
            self.machine_instance_readymat.display_name,
            f'[{self.machine_instance_readymat.name}] '
            f'{self.machine_instance_readymat.ip}',
        )

    def test_03_machine_url(self):
        """Check URL when no protocol is specified."""
        self.assertFalse(self.machine_instance_wood.url)

    def test_04_machine_url(self):
        """Set http protocol, then unset domain."""
        self.machine_instance_wood.http_protocol = 'http'
        self.assertEqual(
            self.machine_instance_wood.url,
            f'http://{self.machine_instance_wood.domain}',
        )
        self.machine_instance_wood.domain = False
        self.assertFalse(self.machine_instance_wood.url)

    def test_05_machine_url(self):
        """Set https protocol."""
        self.machine_instance_wood.http_protocol = 'https'
        self.assertEqual(
            self.machine_instance_wood.url,
            f'https://{self.machine_instance_wood.domain}',
        )

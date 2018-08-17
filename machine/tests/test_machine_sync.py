from . import common


class TestMachineSync(common.TestMachineCommon):
    """Class to test parameter fields sync between machines.

    Syncing is done by propagating template parameter fields changes to
    its instances (if template and its instance has syncing enabled).
    """

    @classmethod
    def setUpClass(cls):
        """Set up common sync field values dict."""
        super(TestMachineSync, cls).setUpClass()
        cls.sync_vals = {
            'is_virtual': True,
            'is_container': True,
            'amount_storage_capacity': 100.0,
            'amount_ram': 3.0,
            'cpu_id': 2,
            'os_id': 2,
        }

    def test_filter_sync_1(self):
        """Change amount_storage_capacity and amount_ram.

        Change it for machine_template_1.
        """
        # Write vals are filtered to fields that can be synced with
        # instances, including filter on template itself.
        res = self.machine_template_1._filter_sync_values({
            'name': 'some new name',
            'amount_storage_capacity': 100.0,
            'amount_ram': 2.0}
        )
        self.assertEqual(
            res, {'amount_storage_capacity': 100.0, 'amount_ram': 2.0})

    def test_filter_sync_2(self):
        """Change all possible fields that can be synced."""
        res = self.machine_template_1._filter_sync_values(self.sync_vals)
        self.assertEqual(
            res, self.sync_vals)

    def test_filter_sync_4(self):
        """Filter sync values on template without sync enabled."""
        res = self.machine_template_2._filter_sync_values(self.sync_vals)
        self.assertEqual(res, {})

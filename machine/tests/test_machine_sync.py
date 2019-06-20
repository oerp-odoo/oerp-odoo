from odoo.exceptions import ValidationError

from . import common


class TestMachineSync(common.TestMachineCommon):
    """Class to test parameter fields sync between machines.

    Syncing is done by propagating template parameter fields changes to
    its instances (if template and its instance has syncing enabled).
    """

    @staticmethod
    def _sorted(record):
        return record.sorted(key=lambda r: r.id)

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

    def test_filter_sync_3(self):
        """Filter empty sync values."""
        res = self.machine_template_2._filter_sync_values({})
        self.assertEqual(res, {})

    def test_get_sync_instances_1(self):
        """Get sync instances for machine_template_1."""
        res = self.machine_template_1._get_sync_instances()
        self.assertEqual(
            self._sorted(res), self._sorted(self.mit_1_1 | self.mit_1_2))

    def test_get_sync_instances_2(self):
        """Get sync instances for machine_template_2."""
        res = self.machine_template_2._get_sync_instances()
        self.assertEqual(res, self.MachineInstance)

    def test_get_sync_instances_3(self):
        """Get sync instances for machine instance (non template)."""
        res = self.mit_1_1._get_sync_instances()
        self.assertEqual(res, self.MachineInstance)

    def test_get_sync_instances_4(self):
        """Get sync instances for machine_template_1/2."""
        templates = self.machine_template_1 | self.machine_template_2
        res = templates._get_sync_instances()
        self.assertEqual(
            self._sorted(res), self._sorted(self.mit_1_1 | self.mit_1_2))

    def _test_sync(self, instances, vals):
        instances_vals = instances.read(fields=vals.keys(), load=False)
        for instance_vals in instances_vals:
            instance_vals.pop('id')
            self.assertEqual(instance_vals, vals)

    def test_sync_1(self):
        """Change machine_template_1 to sync with instances."""
        expected_vals = {
            'is_virtual': True,
            'is_container': False,
            # Expecting that only amount_storage_capacity and amount_ram
            # will be changed.
            'amount_storage_capacity': 200.0,
            'amount_ram': 5,
            'cpu_id': 1,
            'os_id': 2,
        }
        self.machine_template_1.write(
            {
                'amount_ram': 5,
                'amount_storage_capacity': 200,
                'name': 'Production 2'}
        )
        self.assertEqual(self.machine_template_1.name, 'Production 2')
        self._test_sync(
            self.machine_template_1 | self.mit_1_1 | self.mit_1_2,
            expected_vals)
        self.assertEqual(self.mit_1_1.name, 'Wood Corner Production')
        self.assertEqual(self.mit_1_2.name, 'Deco Addict Production')
        # Update expected values, because we do not expect mit_1_3 to
        # be synchronized.
        expected_vals.update(amount_storage_capacity=30, amount_ram=8)
        self._test_sync(self.mit_1_3, expected_vals)
        self.assertEqual(self.mit_1_3.name, 'Gemini Furniture Production')

    def test_sync_2(self):
        """Change machine_template_2 to sync with instances."""
        # We expect no changes from machine_template_2 instance, because
        # no sync is enabled.
        expected_vals = {
            'is_virtual': True,
            'is_container': False,
            # Expecting that only amount_storage_capacity and amount_ram
            # will be changed.
            'amount_storage_capacity': 200.0,
            'amount_ram': 5,
            'cpu_id': 2,
            'os_id': 8,
        }
        self.machine_template_2.write(
            {
                'amount_ram': 5,
                'amount_storage_capacity': 200,
                'name': 'Experimental 2'}
        )
        self.assertEqual(self.machine_template_2.name, 'Experimental 2')
        self._test_sync(self.machine_template_2, expected_vals)
        # Update expected_vals for mit_2_1 (because it should not be
        # changed).
        expected_vals.update(amount_storage_capacity=40.0, amount_ram=4.0)
        self._test_sync(self.mit_2_1, expected_vals)
        self.assertEqual(self.mit_2_1.name, 'Ready Mat Experimental')

    def test_sync_3(self):
        """Try to change synced fields on machine instance.

        Case: sync is enabled.
        """
        self.assertRaises(
            ValidationError, self.mit_1_1.write, {'amount_ram': 10.0})

    def test_sync_4(self):
        """Try to change synced fields on machine instance.

        Case: sync is disabled.
        """
        try:
            self.mit_1_3.amount_ram = 5.0
        except ValidationError:
            self.fail(
                "When sync is disabled, it should allow changing synced field"
                " on instance.")

from ..tools.record import cleanup_noop_values
from . import common


class TestRecordCleanupNoopValues(common.TestOdootilCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1, cls.partner_2 = cls.ResPartner.create(
            [
                {'name': 'MY-PARTNER-1'},
                {'name': 'MY-PARTNER-2'},
            ]
        )

    def test_01_cleanup_noop_values(self):
        # GIVEN
        vals = {'name': 'MY-PARTNER-1'}
        # WHEN
        cleanup_noop_values(self.partner_1, vals)
        # THEN
        self.assertEqual(vals, {})

    def test_02_cleanup_noop_values_empty_recordset(self):
        # GIVEN
        vals = {'name': 'MY-PARTNER-1'}
        # WHEN
        cleanup_noop_values(self.ResPartner, vals)
        # THEN
        self.assertEqual(vals, {'name': 'MY-PARTNER-1'})

    def test_03_cleanup_noop_values_empty_dict(self):
        # GIVEN
        vals = {}
        # WHEN
        cleanup_noop_values(self.partner_1, vals)
        # THEN
        self.assertEqual(vals, {})

    def test_04_cleanup_noop_values_multi(self):
        # GIVEN
        vals = {'name': 'MY-PARTNER-1'}
        self.partner_2.name = 'MY-PARTNER-1'
        # WHEN
        cleanup_noop_values(self.partner_1 | self.partner_2, vals)
        # THEN
        self.assertEqual(vals, {})

    def test_05_cleanup_noop_values_no_match(self):
        # GIVEN
        vals = {'name': 'MY-PARTNER-111'}
        # WHEN
        cleanup_noop_values(self.partner_1, vals)
        # THEN
        self.assertEqual(vals, {'name': 'MY-PARTNER-111'})

    def test_06_cleanup_noop_values_multi_no_match(self):
        # GIVEN
        vals = {'name': 'MY-PARTNER-1'}
        # WHEN
        cleanup_noop_values(self.partner_1 | self.partner_2, vals)
        # THEN
        self.assertEqual(vals, {'name': 'MY-PARTNER-1'})

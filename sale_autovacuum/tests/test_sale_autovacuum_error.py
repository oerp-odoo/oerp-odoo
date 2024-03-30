from odoo.tools import mute_logger

from .common import TestSaleAutovacuumCommon


def action_autovacuum_cancel_patched(self, sales):
    raise ValueError("Failed!")


class TestSaleAutovacuumError(TestSaleAutovacuumCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleAutovacuumRule._patch_method(
            '_action_autovacuum_cancel', action_autovacuum_cancel_patched
        )

    @mute_logger('odoo.addons.sale_autovacuum.models.sale_autovacuum_rule')
    def test_01_autovacuum_force_error_on_cancel(self):
        # GIVEN.
        self.sale_1.state = 'sent'
        # WHEN
        self.sale_autovac_rule_1.process(
            auto_commit=True, rule_ids=self.sale_autovac_rule_1.ids
        )
        # THEN
        msg = self.sale_autovac_rule_1.message_ids[0]
        self.assertIn('Something went wrong processing sales autovacuum', msg.body)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.SaleAutovacuumRule._revert_method('_action_autovacuum_cancel')

from unittest.mock import patch

from odoo.tools import mute_logger

from .common import TestSaleAutovacuumCommon


class TestSaleAutovacuumError(TestSaleAutovacuumCommon):
    @mute_logger('odoo.addons.sale_autovacuum.models.sale_autovacuum_rule')
    def test_01_autovacuum_force_error_on_cancel(self):
        # GIVEN.
        self.sale_1.state = 'sent'
        # WHEN
        with patch.object(
            type(self.SaleAutovacuumRule), '_action_autovacuum_cancel'
        ) as m:
            m.side_effect = ValueError("Failed")
            self.sale_autovac_rule_1.process(
                auto_commit=True, rule_ids=self.sale_autovac_rule_1.ids
            )
        # THEN
        msg = self.sale_autovac_rule_1.message_ids[0]
        self.assertIn('Something went wrong processing sales autovacuum', msg.body)

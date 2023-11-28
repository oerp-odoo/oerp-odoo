from .common import TestSaleAutovacuumCommon


class TestSaleAutovacuumOk(TestSaleAutovacuumCommon):
    def test_01_find_sales_draft_only_for_cancel(self):
        # GIVEN
        self.sale_2.state = 'sent'
        self.sale_autovac_rule_1.write(
            {
                'days': 100,
                'domain': (
                    f"[('partner_id', '=', {self.partner_1.id}), "
                    + "('state', '=', 'draft')]"
                ),
            }
        )
        # WHEN
        sales = self.sale_autovac_rule_1.find_sale_orders()
        # THEN
        self.assertEqual(sales, self.sale_1)

    def test_02_find_sales_draft_sent_states_for_cancel(self):
        # GIVEN
        self.sale_2.state = 'sent'
        # WHEN
        sales = self.sale_autovac_rule_1.find_sale_orders()
        # THEN
        self.assertCountEqual(sales, self.sale_1 | self.sale_2)

    def test_03_find_sales_draft_only_for_unlink(self):
        # GIVEN
        # When we have unlink action, only draft is allowed.
        self.sale_autovac_rule_1.action = 'unlink'
        self.sale_2.state = 'sent'
        # WHEN
        sales = self.sale_autovac_rule_1.find_sale_orders()
        # THEN
        self.assertEqual(sales, self.sale_1)

    def test_04_autovacuum_cancel(self):
        # GIVEN
        self.sale_autovac_rule_1.action = 'cancel'
        # WHEN
        self.sale_autovac_rule_1.action_autovacuum()
        # THEN
        self.assertEqual(self.sale_1.state, 'cancel')
        self.assertEqual(self.sale_2.state, 'cancel')
        self.assertEqual(self.sale_3.state, 'draft')
        msg = self.sale_autovac_rule_1.message_ids[0]
        self.assertIn("2 sale quote(s) cancelled", msg.body)

    def test_05_autovacuum_unlink(self):
        # GIVEN
        self.sale_autovac_rule_1.action = 'unlink'
        # WHEN
        self.sale_autovac_rule_1.action_autovacuum()
        # THEN
        self.assertFalse(self.sale_1.exists())
        self.assertFalse(self.sale_2.exists())
        self.assertTrue(self.sale_3.exists())
        msg = self.sale_autovac_rule_1.message_ids[0]
        self.assertIn("2 sale quote(s) deleted", msg.body)

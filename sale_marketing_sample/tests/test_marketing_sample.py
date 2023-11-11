from odoo.tests import common


@common.tagged('post_install', '-at_install')
class TestMarketingSample(common.TransactionCase):
    """Test class for marketing sample workflow."""

    @classmethod
    def setUpClass(cls):
        """Set up data for marketing sample tests."""
        super().setUpClass()
        cls.AccountMove = cls.env['account.move']
        cls.sale_1 = cls.env.ref('sale.sale_order_1')
        cls.sale_1.order_line.mapped('product_id').write(
            {
                'invoice_policy': 'order',
            }
        )

    # TODO: redundant, copied from delivery_dhl_extended
    @classmethod
    def _force_picking_done(cls, picking):
        picking.action_assign()
        for move in picking.move_lines.filtered(
            lambda m: m.state not in ['done', 'cancel']
        ):
            for move_line in move.move_line_ids:
                move_line.qty_done = move_line.product_uom_qty
        picking._action_done()

    def test_01_marketing_sample(self):
        """Check SO workflow when is_marketing=True.

        Marketing flags must be passed from SO, to picking, to invoice.
        """
        self.sale_1.is_marketing = True
        self.sale_1.action_confirm()
        picking = self.sale_1.picking_ids[0]
        self.assertTrue(picking.use_selling_price)
        self._force_picking_done(picking)
        account_move = self.sale_1._create_invoices()[0]
        self.assertTrue(account_move.is_marketing)
        account_move.action_post()
        # Must auto pay invoice with is_marketing=True.
        self.assertEqual(account_move.state, 'posted')
        self.assertEqual(account_move.payment_state, 'paid')
        # Run auto pay again, to make sure its ignored now.
        self.assertFalse(account_move._auto_pay_move())

    def test_02_marketing_sample(self):
        """Check SO workflow when is_marketing=False.

        Marketing flags must not be passed from SO, to picking, to
        invoice.
        """
        self.sale_1.action_confirm()
        picking = self.sale_1.picking_ids[0]
        self.assertFalse(picking.use_selling_price)
        self._force_picking_done(picking)
        account_move = self.sale_1._create_invoices()[0]
        self.assertFalse(account_move.is_marketing)
        account_move.action_post()
        self.assertEqual(account_move.state, 'posted')
        self.assertEqual(account_move.payment_state, 'not_paid')

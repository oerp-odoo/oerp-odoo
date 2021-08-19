from odoo.tests import common


class TestSaleAutoLock(common.SavepointCase):
    """Test class for sale order auto lock functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up data for sale order auto lock tests."""
        super().setUpClass()
        cls.SaleOrder = cls.env['sale.order']
        cls.SaleOrderLine = cls.env['sale.order.line']
        cls.sale_1 = cls.env.ref('sale.sale_order_1')
        # Service product.
        cls.product_home_staging = cls.env.ref('product.product_product_2')
        # It makes no sense for service to have delivery invoice policy.
        # It also bugs out invoice_status in Odoo.
        cls.product_home_staging.invoice_policy = 'order'
        # Storable
        cls.product_block_screens = cls.env.ref('product.product_product_25')
        # Keep only block screens product, because others are out of
        # stock.
        lines_to_unlink = cls.sale_1.order_line.filtered(
            lambda r: r.product_id != cls.product_block_screens
        )
        lines_to_unlink.unlink()
        cls.sale_1_line_service = cls.SaleOrderLine.create({
            'order_id': cls.sale_1.id,
            'product_id': cls.product_home_staging.id,
            'product_uom_id': cls.product_home_staging.uom_id.id,
            'product_uom_qty': 1,
            'price_unit': 100,
        })

    def test_01_find_and_lock_orders(self):
        """Try and lock order in various conditions.

        Last case locks order.

        Case 1: SO not confirmed.
        Case 2: no picking, invoice done.
        Case 3: picking done, but invoice not.
        Case 4: all documents done.
        """
        # Case 1.
        domain = [('id', '=', self.sale_1.id)]
        res = self.SaleOrder._find_and_lock_orders(args=domain)
        self.assertEqual(res, self.SaleOrder)
        self.assertEqual(self.sale_1.state, 'draft')
        # Case 2.
        self.sale_1.action_confirm()
        res = self.SaleOrder._find_and_lock_orders(args=domain)
        self.assertEqual(res, self.SaleOrder)
        # Case 3.
        picking = self.sale_1.picking_ids[0]
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        res = self.SaleOrder._find_and_lock_orders(args=domain)
        self.assertEqual(res, self.SaleOrder)
        # Case 4.
        invoice_ids = self.sale_1.action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_ids)
        invoice.action_invoice_open()
        # We only care if state is paid.
        invoice.state = 'paid'
        res = self.SaleOrder._find_and_lock_orders(args=domain)
        self.assertEqual(res, self.sale_1)
        self.assertEqual(self.sale_1.state, 'done')

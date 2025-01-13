from odoo.addons.base.tests.common import BaseCommon


class TestSaleDeliveryProgress(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.ProcurementGroup = cls.env['procurement.group']
        cls.SaleOrder = cls.env['sale.order']
        cls.SaleOrderLine = cls.env['sale.order.line']
        cls.ProductProduct = cls.env['product.product']
        cls.product_1, cls.product_2 = cls.ProductProduct.create(
            [
                {'name': 'MY-PRODUCT-1', 'type': 'product'},
                {'name': 'MY-PRODUCT-2', 'type': 'product'},
            ]
        )
        cls.partner_customer = cls.ResPartner.create({'name': 'MY-CUSTOMER-1'})
        cls.procurement_group_1 = cls.ProcurementGroup.create(
            {'name': 'MY-PROCUREMENT-GROUP-1'}
        )
        cls.sale_1 = cls.SaleOrder.create({'partner_id': cls.partner_customer.id})
        cls.sale_1_line_1, cls.sale_1_line_2 = cls.SaleOrderLine.create(
            [
                {
                    'order_id': cls.sale_1.id,
                    'product_id': cls.product_1.id,
                    'price_unit': 10,
                    'product_uom_qty': 10,
                },
                {
                    'order_id': cls.sale_1.id,
                    'product_id': cls.product_2.id,
                    'price_unit': 20,
                    'product_uom_qty': 20,
                },
            ]
        )
        cls.sale_1.procurement_group_id = cls.procurement_group_1.id
        cls.procurement_group_1.sale_id = cls.sale_1.id

    def test_01_delivery_progress_no_pickings(self):
        self.assertEqual(self.sale_1.delivery_progress, 0)
        self.assertEqual(len(self.sale_1.picking_ids), 0)

    def test_02_delivery_progress_no_pickings_finished(self):
        # WHEN
        self.sale_1.action_confirm()
        # THEN
        self.assertEqual(self.sale_1.delivery_progress, 0)
        self.assertEqual(len(self.sale_1.picking_ids), 1)

    def test_03_delivery_progress_one_of_two_done(self):
        # GIVEN
        self.sale_1.action_confirm()
        picking_1 = self.sale_1.picking_ids
        picking_2 = picking_1.copy()
        # WHEN
        picking_2.state = 'done'
        # THEN
        self.assertEqual(self.sale_1.delivery_progress, 50)
        self.assertEqual(len(self.sale_1.picking_ids), 2)

    def test_04_delivery_progress_all_done(self):
        # GIVEN
        self.sale_1.action_confirm()
        picking_1 = self.sale_1.picking_ids
        picking_2 = picking_1.copy()
        # WHEN
        (picking_1 | picking_2).write({'state': 'done'})
        # THEN
        self.assertEqual(self.sale_1.delivery_progress, 100)
        self.assertEqual(len(self.sale_1.picking_ids), 2)

    def test_05_delivery_progress_all_finished(self):
        # GIVEN
        self.sale_1.action_confirm()
        picking_1 = self.sale_1.picking_ids
        picking_2 = picking_1.copy()
        # WHEN
        picking_1.state = 'done'
        picking_2.state = 'cancel'
        # THEN
        self.assertEqual(self.sale_1.delivery_progress, 100)
        self.assertEqual(len(self.sale_1.picking_ids), 2)

    def test_06_delivery_progress_all_cancelled(self):
        # GIVEN
        self.sale_1.action_confirm()
        picking_1 = self.sale_1.picking_ids
        picking_2 = picking_1.copy()
        # WHEN
        (picking_1 | picking_2).write({'state': 'cancel'})
        # THEN
        self.assertEqual(self.sale_1.delivery_progress, 100)
        self.assertEqual(len(self.sale_1.picking_ids), 2)

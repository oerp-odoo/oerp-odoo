from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSalePurchaseStatus(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.ProcurementGroup = cls.env['procurement.group']
        cls.SaleOrder = cls.env['sale.order']
        cls.SaleOrderLine = cls.env['sale.order.line']
        cls.ProductProduct = cls.env['product.product']
        cls.PurchaseOrder = cls.env['purchase.order']
        cls.warehouse_1 = cls.env.ref('stock.warehouse0')
        cls.product_1, cls.product_2 = cls.ProductProduct.create(
            [
                {'name': 'MY-PRODUCT-1', 'type': 'product'},
                {'name': 'MY-PRODUCT-2', 'type': 'product'},
            ]
        )
        cls.partner_customer, cls.partner_vendor = cls.ResPartner.create(
            [{'name': 'MY-CUSTOMER-1'}, {'name': 'MY-VENDOR-1'}]
        )
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

    def test_01_purchase_status_no_purchases(self):
        # GIVEN
        po = self.PurchaseOrder.create(
            {
                'partner_id': self.partner_vendor.id,
                'group_id': self.procurement_group_1.id,
            }
        )
        # WHEN
        # Cancelled POs must be ignored.
        po.button_cancel()
        # THEN
        self.assertEqual(self.sale_1.purchase_status, False)
        self.assertEqual(len(self.sale_1.picking_from_primary_ids), 0)

    def test_02_purchase_status_rfq(self):
        # WHEN
        _po_1, po_2 = self.PurchaseOrder.create(
            [
                {
                    'partner_id': self.partner_vendor.id,
                    'group_id': self.procurement_group_1.id,
                },
                {
                    'partner_id': self.partner_vendor.id,
                    'group_id': self.procurement_group_1.id,
                },
            ],
        )
        # WHEN
        po_2.button_confirm()
        # THEN
        self.assertEqual(self.sale_1.purchase_status, 'rfq')
        # 0 because POs have no lines, so pickings won't be created.
        self.assertEqual(len(self.sale_1.picking_from_primary_ids), 0)

    def test_03_purchase_status_confirmed_one_step(self):
        # GIVEN
        po = self.PurchaseOrder.create(
            {
                'partner_id': self.partner_vendor.id,
                'group_id': self.procurement_group_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': self.product_1.id,
                            'price_unit': 10,
                            'product_qty': 10,
                        }
                    ),
                    Command.create(
                        {
                            'product_id': self.product_2.id,
                            'price_unit': 20,
                            'product_qty': 20,
                        }
                    ),
                ],
            }
        )
        # WHEN
        po.button_confirm()
        # THEN
        self.assertEqual(self.sale_1.purchase_status, 'confirmed')
        self.assertEqual(len(self.sale_1.picking_from_primary_ids), 1)

    def test_04_purchase_status_confirmed_two_steps(self):
        # GIVEN
        self.warehouse_1.reception_steps = 'two_steps'
        po = self.PurchaseOrder.create(
            {
                'partner_id': self.partner_vendor.id,
                'group_id': self.procurement_group_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': self.product_1.id,
                            'price_unit': 10,
                            'product_qty': 10,
                        }
                    ),
                    Command.create(
                        {
                            'product_id': self.product_2.id,
                            'price_unit': 20,
                            'product_qty': 20,
                        }
                    ),
                ],
            }
        )
        # WHEN
        po.button_confirm()
        # THEN
        self.assertEqual(self.sale_1.purchase_status, 'confirmed')
        self.assertEqual(len(self.sale_1.picking_from_primary_ids), 2)

    def test_05_purchase_status_received_two_steps(self):
        # GIVEN
        self.warehouse_1.reception_steps = 'two_steps'
        po = self.PurchaseOrder.create(
            {
                'partner_id': self.partner_vendor.id,
                'group_id': self.procurement_group_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': self.product_1.id,
                            'price_unit': 10,
                            'product_qty': 10,
                        }
                    ),
                    Command.create(
                        {
                            'product_id': self.product_2.id,
                            'price_unit': 20,
                            'product_qty': 20,
                        }
                    ),
                ],
            }
        )
        po.button_confirm()
        input_picking = po.picking_ids[0]
        # WHEN
        input_picking.button_validate()
        # THEN
        self.assertEqual(self.sale_1.purchase_status, 'received')
        self.assertEqual(len(self.sale_1.picking_from_primary_ids), 2)

    def test_06_purchase_status_done_one_step(self):
        # GIVEN
        po = self.PurchaseOrder.create(
            {
                'partner_id': self.partner_vendor.id,
                'group_id': self.procurement_group_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': self.product_1.id,
                            'price_unit': 10,
                            'product_qty': 10,
                        }
                    ),
                    Command.create(
                        {
                            'product_id': self.product_2.id,
                            'price_unit': 20,
                            'product_qty': 20,
                        }
                    ),
                ],
            }
        )
        po.button_confirm()
        picking = po.picking_ids[0]
        # WHEN
        picking.button_validate()
        # THEN
        self.assertEqual(self.sale_1.purchase_status, 'done')
        self.assertEqual(len(self.sale_1.picking_from_primary_ids), 1)

    def test_07_purchase_status_done_two_steps(self):
        # GIVEN
        self.warehouse_1.reception_steps = 'two_steps'
        po = self.PurchaseOrder.create(
            {
                'partner_id': self.partner_vendor.id,
                'group_id': self.procurement_group_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': self.product_1.id,
                            'price_unit': 10,
                            'product_qty': 10,
                        }
                    ),
                    Command.create(
                        {
                            'product_id': self.product_2.id,
                            'price_unit': 20,
                            'product_qty': 20,
                        }
                    ),
                ],
            }
        )
        po.button_confirm()
        input_picking = po.picking_ids[0]
        input_to_stock_picking = self.sale_1.picking_from_primary_ids[0]
        # WHEN
        # Must validate one after another instead of together, because
        # input_to_stock_picking depends on input_picking.
        input_picking.button_validate()
        input_to_stock_picking.button_validate()
        # THEN
        self.assertEqual(self.sale_1.purchase_status, 'done')
        self.assertEqual(len(self.sale_1.picking_from_primary_ids), 2)

from odoo.addons.base.tests.common import BaseCommon


class TestSaleProductionProgress(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.ProcurementGroup = cls.env['procurement.group']
        cls.SaleOrder = cls.env['sale.order']
        cls.SaleOrderLine = cls.env['sale.order.line']
        cls.ProductProduct = cls.env['product.product']
        cls.MrpProduction = cls.env['mrp.production']
        cls.MrpBom = cls.env['mrp.bom']
        cls.product_1, cls.product_2 = cls.ProductProduct.create(
            [
                {'name': 'MY-PRODUCT-1', 'type': 'product'},
                {'name': 'MY-PRODUCT-2', 'type': 'product'},
            ]
        )
        cls.bom_1, cls.bom_2 = cls.MrpBom.create(
            [
                {'product_tmpl_id': cls.product_1.product_tmpl_id.id},
                {'product_tmpl_id': cls.product_2.product_tmpl_id.id},
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

    def test_01_production_progress_no_mos(self):
        self.assertEqual(self.sale_1.production_progress, 0)
        self.assertEqual(len(self.sale_1.production_from_primary_ids), 0)

    def test_02_production_progress_no_mo_finished(self):
        # WHEN
        self.MrpProduction.create(
            [
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
            ],
        )
        # WHEN
        # THEN
        self.assertEqual(self.sale_1.production_progress, 0)
        self.assertEqual(len(self.sale_1.production_from_primary_ids), 1)

    def test_03_production_progress_one_of_two_done(self):
        # WHEN
        mos = self.MrpProduction.create(
            [
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
                {
                    'product_id': self.product_2.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
            ],
        )
        # WHEN
        mos[0].state = 'done'
        # THEN
        self.assertEqual(self.sale_1.production_progress, 50)
        self.assertEqual(len(self.sale_1.production_from_primary_ids), 2)

    def test_04_production_progress_all_done(self):
        # WHEN
        mos = self.MrpProduction.create(
            [
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
                {
                    'product_id': self.product_2.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
            ],
        )
        # WHEN
        mos.write({'state': 'done'})
        # THEN
        self.assertEqual(self.sale_1.production_progress, 100)
        self.assertEqual(len(self.sale_1.production_from_primary_ids), 2)

    def test_04_production_progress_all_finished(self):
        # WHEN
        mo_1, mo_2 = self.MrpProduction.create(
            [
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
                {
                    'product_id': self.product_2.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
            ],
        )
        # WHEN
        mo_1.state = 'done'
        mo_2.state = 'cancel'
        # THEN
        self.assertEqual(self.sale_1.production_progress, 100)
        self.assertEqual(len(self.sale_1.production_from_primary_ids), 2)

    def test_05_production_progress_all_cancelled(self):
        # WHEN
        mos = self.MrpProduction.create(
            [
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
                {
                    'product_id': self.product_2.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
            ],
        )
        # WHEN
        mos.write({'state': 'cancel'})
        # THEN
        self.assertEqual(self.sale_1.production_progress, 100)
        self.assertEqual(len(self.sale_1.production_from_primary_ids), 2)

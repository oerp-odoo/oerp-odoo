from odoo.tests.common import TransactionCase


class TestSaleGroupNameMrpPurchase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.ProductCategory = cls.env['product.category']
        cls.ProductProduct = cls.env['product.product']
        cls.SaleOrder = cls.env['sale.order']
        cls.MrpBom = cls.env['mrp.bom']
        cls.MrpProduction = cls.env['mrp.production']
        cls.PurchaseOrder = cls.env['purchase.order']
        cls.stock_route_mto = cls.env.ref('stock.route_warehouse0_mto')
        cls.stock_route_mto.active = True
        cls.stock_route_buy = cls.env.ref('purchase_stock.route_warehouse0_buy')
        cls.stock_route_manufacture = cls.env.ref('mrp.route_warehouse0_manufacture')
        cls.partner_1, cls.partner_vendor_1 = cls.ResPartner.create(
            [
                {'name': 'MY-PARTNER-1', 'is_company': True},
                {'name': 'MY-VENDOR-1', 'is_company': True},
            ]
        )
        (cls.product_1, cls.product_1_comp_1,) = cls.ProductProduct.create(
            [
                {
                    'name': 'P1',
                    'route_ids': [
                        (4, cls.stock_route_mto.id),
                        (4, cls.stock_route_manufacture.id),
                    ],
                },
                {
                    'name': 'P1-COMPONENT-1',
                    'seller_ids': [(0, 0, {'partner_id': cls.partner_vendor_1.id})],
                    'route_ids': [
                        (4, cls.stock_route_mto.id),
                        (4, cls.stock_route_buy.id),
                    ],
                },
            ]
        )
        cls.bom_1 = cls.MrpBom.create(
            {
                'product_tmpl_id': cls.product_1.product_tmpl_id.id,
                'bom_line_ids': [(0, 0, {'product_id': cls.product_1_comp_1.id})],
            }
        )
        cls.sale_1 = cls.SaleOrder.create({'partner_id': cls.partner_1.id})

    def test_01_sale_group_name_mrp_purchase_linked_single_line_no_packaging_name(self):
        # GIVEN
        self.sale_1.order_line = [
            (
                0,
                0,
                {
                    'group_name': 'A-1',
                    'product_id': self.product_1.id,
                    'product_uom_qty': 1,
                },
            )
        ]
        # WHEN
        self.sale_1.action_confirm()
        # THEN
        mo = self.MrpProduction.search([('origin', '=', self.sale_1.name)])
        self.assertEqual(len(mo), 1)
        purchase = self.PurchaseOrder.search([('origin', '=', mo.name)])
        self.assertEqual(len(purchase), 1)
        self.assertEqual(mo.sale_group_name, 'A-1')
        self.assertEqual(
            purchase.order_line[0].component_sticker_info, f'A-1, {self.sale_1.name}'
        )

    def test_02_sale_group_name_mrp_purchase_linked_multi_line_w_packaging_name(self):
        # GIVEN
        pname = 'PNAME01'
        self.product_1.packaging_name = pname
        self.sale_1.order_line = [
            (
                0,
                0,
                {
                    'group_name': 'A-1',
                    'product_id': self.product_1.id,
                    # NOTE. Quantity on line means nothing when
                    # deciding how to generate a sticker info for now.
                    'product_uom_qty': 2,
                },
            ),
            (
                0,
                0,
                {
                    'group_name': 'A-2',
                    'product_id': self.product_1.id,
                    'product_uom_qty': 1,
                },
            ),
        ]
        # WHEN
        self.sale_1.action_confirm()
        # THEN
        mos = self.MrpProduction.search([('origin', '=', self.sale_1.name)])
        self.assertEqual(len(mos), 2)
        self.assertEqual(set(mos.mapped('sale_group_name')), {'A-1', 'A-2'})
        purchase = self.PurchaseOrder.search(
            [
                '|',
                ('origin', 'like', f'%{mos[0].name}%'),
                ('origin', 'like', f'%{mos[1].name}%'),
            ]
        )
        self.assertEqual(len(purchase), 1)
        sale_name = self.sale_1.name
        self.assertEqual(
            purchase.order_line[0].component_sticker_info,
            f'A-1, {pname}, {sale_name}; A-2, {pname}, {sale_name}',
        )

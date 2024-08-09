from odoo.tests.common import TransactionCase


class TestSaleMrpSaleOrigin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.ProductProduct = cls.env['product.product']
        cls.SaleOrder = cls.env['sale.order']
        cls.MrpBom = cls.env['mrp.bom']
        cls.MrpProduction = cls.env['mrp.production']
        cls.stock_route_mto = cls.env.ref('stock.route_warehouse0_mto')
        cls.stock_route_mto.active = True
        cls.stock_route_manufacture = cls.env.ref('mrp.route_warehouse0_manufacture')
        cls.partner_1 = cls.ResPartner.create(
            [
                {'name': 'MY-PARTNER-1', 'is_company': True},
            ]
        )
        (
            cls.product_1,
            cls.product_1_comp_1,
        ) = cls.ProductProduct.create(
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
                    'route_ids': [
                        (4, cls.stock_route_mto.id),
                        (4, cls.stock_route_manufacture.id),
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
        cls.sale_1 = cls.SaleOrder.create(
            {'partner_id': cls.partner_1.id, 'origin': 'SO-ORIGIN-1'}
        )

    def test_01_mrp_sale_origin_multi_level_boms(self):
        # GIVEN
        self.sale_1.order_line = [
            (
                0,
                0,
                {
                    'product_id': self.product_1.id,
                    'product_uom_qty': 1,
                },
            )
        ]
        # WHEN
        self.sale_1.action_confirm()
        # THEN
        mo = self.MrpProduction.search([('sale_origin', '=', 'SO-ORIGIN-1')])
        self.assertEqual(len(mo), 1)
        mo_main = mo.filtered(lambda r: r.product_id == self.product_1)
        self.assertEqual(len(mo_main), 1)

from odoo.fields import Command
from odoo.tests import TransactionCase


class TestMrpUnbuildMulti(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.MrpProduction = cls.env['mrp.production']
        cls.StockQuant = cls.env['stock.quant']
        cls.MrpBom = cls.env['mrp.bom']
        cls.MrpUnbuild = cls.env['mrp.unbuild']
        cls.MrpUnbuildMulti = cls.env['mrp.unbuild.multi']
        cls.MrpUnbuildMultiSummary = cls.env['mrp.unbuild.multi.summary']
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.stock_route_mto = cls.env.ref('stock.route_warehouse0_mto')
        cls.stock_route_mto.active = True
        cls.stock_route_manufacture = cls.env.ref('mrp.route_warehouse0_manufacture')
        cls.product_1, cls.product_2, cls.product_component = cls.ProductProduct.create(
            [
                {
                    'name': 'MY-PRODUCT-1',
                    'is_storable': True,
                    'route_ids': [
                        Command.link(cls.stock_route_mto.id),
                        Command.link(cls.stock_route_manufacture.id),
                    ],
                },
                {
                    'name': 'MY-PRODUCT-2',
                    'is_storable': True,
                    'route_ids': [
                        Command.link(cls.stock_route_mto.id),
                        Command.link(cls.stock_route_manufacture.id),
                    ],
                },
                {
                    'name': 'MY-PRODUCT-COMPONENT-1',
                    'is_storable': True,
                },
            ]
        )
        cls.StockQuant.create(
            [
                {
                    'product_id': cls.product_1.id,
                    'location_id': cls.stock_location.id,
                    'quantity': 100,
                },
                {
                    'product_id': cls.product_2.id,
                    'location_id': cls.stock_location.id,
                    'quantity': 100,
                },
                {
                    'product_id': cls.product_component.id,
                    'location_id': cls.stock_location.id,
                    'quantity': 100,
                },
            ]
        )

    def test_01_unbuild_multi_mo_independent(self):
        # GIVEN
        self.MrpBom.create(
            [
                {
                    'product_tmpl_id': self.product_1.product_tmpl_id.id,
                    'bom_line_ids': [(0, 0, {'product_id': self.product_component.id})],
                },
                {
                    'product_tmpl_id': self.product_2.product_tmpl_id.id,
                    'bom_line_ids': [(0, 0, {'product_id': self.product_component.id})],
                },
            ]
        )
        mos = self.MrpProduction.create(
            [
                {'product_id': self.product_1.id, 'product_qty': 1},
                {'product_id': self.product_2.id, 'product_qty': 2},
            ]
        )
        mos.action_confirm()
        mos.button_mark_done()
        wiz = self.MrpUnbuildMulti.with_context(
            active_ids=mos.ids,
            active_model='mrp.production',
        ).create({})
        # WHEN
        wiz.action_unbuild_multi()
        # THEN
        unbuilds = self.MrpUnbuild.search(
            [('mo_id', 'in', mos.ids)],
        )
        self.assertEqual(len(unbuilds), 2)
        for unbuild in unbuilds:
            self.assertEqual(unbuild.state, 'done', unbuild.mo_id.product_id.name)

    def test_02_unbuild_multi_mo_with_child(self):
        # GIVEN
        self.MrpBom.create(
            [
                {
                    'product_tmpl_id': self.product_1.product_tmpl_id.id,
                    'bom_line_ids': [(0, 0, {'product_id': self.product_2.id})],
                },
                {
                    'product_tmpl_id': self.product_2.product_tmpl_id.id,
                    'bom_line_ids': [(0, 0, {'product_id': self.product_component.id})],
                },
            ]
        )
        mo = self.MrpProduction.create(
            [
                {'product_id': self.product_1.id, 'product_qty': 2},
            ]
        )
        mo.action_confirm()
        mo_child = mo.production_group_id.child_ids.production_ids
        mo_child.action_confirm()
        (mo | mo_child).button_mark_done()
        wiz = self.MrpUnbuildMulti.with_context(
            active_ids=mo.ids,
            active_model='mrp.production',
        ).create({'include_from_group': True})
        # WHEN
        wiz.action_unbuild_multi()
        # THEN
        unbuilds = self.MrpUnbuild.search(
            [('mo_id', 'in', (mo | mo_child).ids)],
        )
        # 1 MO with 1 child.
        self.assertEqual(len(unbuilds), 2)
        for unbuild in unbuilds:
            self.assertEqual(unbuild.state, 'done', unbuild.mo_id.product_id.name)

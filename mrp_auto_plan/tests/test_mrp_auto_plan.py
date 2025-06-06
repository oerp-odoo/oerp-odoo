from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestMrpAutoPlan(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.MrpBom = cls.env['mrp.bom']
        cls.MrpProduction = cls.env['mrp.production']
        (cls.product_1, cls.product_1_comp_1,) = cls.ProductProduct.create(
            [
                {'name': 'P1'},
                {'name': 'P1-COMPONENT-1'},
            ]
        )
        cls.bom_1 = cls.MrpBom.create(
            {
                'product_tmpl_id': cls.product_1.product_tmpl_id.id,
                'product_qty': 1,
                'bom_line_ids': [
                    (0, 0, {'product_id': cls.product_1_comp_1.id, 'product_qty': 2})
                ],
            }
        )

    def test_01_mrp_auto_plan(self):
        # GIVEN
        self.bom_1.auto_plan = True
        # WHEN
        with patch(
            'odoo.addons.mrp.models.mrp_production.MrpProduction.button_plan'
        ) as m:
            self.MrpProduction.create(
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                }
            )
            # THEN
            self.assertEqual(m.call_count, 1)

    def test_02_mrp_auto_plan_disabled(self):
        # GIVEN
        self.bom_1.auto_plan = False
        # WHEN
        with patch(
            'odoo.addons.mrp.models.mrp_production.MrpProduction.button_plan'
        ) as m:
            self.MrpProduction.create(
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                }
            )
            # THEN
            self.assertEqual(m.call_count, 0)

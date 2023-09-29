from odoo.addons.product_stamp_configurator.tests.common import (
    TestProductStampConfiguratorCommon,
)


class TestStampConfigureSaleCrm(TestProductStampConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.CrmLead = cls.env['crm.lead']
        cls.sale_1 = cls.env.ref('sale.sale_order_1')
        cls.sale_2 = cls.sale_1.copy()
        cls.partner_deco_fletcher = cls.env.ref('base.res_partner_address_3')
        # Clear lines to make it more convenient to test it.
        (cls.sale_1 | cls.sale_2).order_line.unlink()
        cls.opp_1 = cls.CrmLead.create({'name': 'My Opp 1', 'type': 'opportunity'})
        (cls.sale_1 | cls.sale_2).write({'opportunity_id': cls.opp_1.id})

    def test_01_multi_stamp_configure_on_sale_and_opp_insert_die_ref(self):
        # GIVEN

        product_ref_1, product_ref_2 = self.ProductProduct.create(
            [
                {
                    'name': 'Die Ref 1',
                    'default_code': '1111F1B7 / 2222',
                    'stamp_type': 'die',
                },
                {
                    'name': 'Die Ref 2',
                    'default_code': '1111F2B7 / 2222',
                    'stamp_type': 'die',
                },
            ]
        )
        ctx = self.sale_1.action_open_stamp_configurator()['context']
        cfg_1 = self.StampConfigure.with_context(**ctx).create(
            {
                'die_id': self.stamp_die_insert.id,
                'product_insert_die_ref_id': product_ref_1.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'material_counter_id': self.stamp_material_plastic_05.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 10,
                'quantity_spare_dies': 3,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
                'quantity_mold': 1,
            }
        )
        cfg_1._onchange_design_id()
        # WHEN
        res = cfg_1._onchange_die_id()
        # THEN
        # Reference product is not set on related sale order line.
        self.assertEqual(
            res['domain']['product_insert_die_ref_id'],
            [('stamp_type', '=', 'die'), ('is_insert_die', '=', False)],
        )
        # WHEN
        self.sale_1.order_line = [
            (
                0,
                0,
                {
                    'product_id': product_ref_1.id,
                    'price_unit': 10,
                    'product_uom_qty': 5,
                },
            )
        ]
        res = cfg_1._onchange_die_id()
        # THEN
        self.assertEqual(
            res['domain']['product_insert_die_ref_id'],
            [
                ('stamp_type', '=', 'die'),
                ('is_insert_die', '=', False),
                ('id', 'in', [product_ref_1.id]),
            ],
        )
        # WHEN
        self.sale_2.order_line = [
            (
                0,
                0,
                {
                    'product_id': product_ref_2.id,
                    'price_unit': 10,
                    'product_uom_qty': 5,
                },
            )
        ]
        res = cfg_1._onchange_die_id()
        # THEN
        id_leaf = res['domain']['product_insert_die_ref_id'].pop()
        self.assertEqual(
            res['domain']['product_insert_die_ref_id'],
            [
                ('stamp_type', '=', 'die'),
                ('is_insert_die', '=', False),
            ],
        )
        self.assertEqual(
            sorted(id_leaf[2]), sorted([product_ref_1.id, product_ref_2.id])
        )

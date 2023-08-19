from odoo.addons.product_stamp_configurator.tests.common import (
    TestProductStampConfiguratorCommon,
)


class TestStampConfigureSale(TestProductStampConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_1 = cls.env.ref('sale.sale_order_1')
        cls.partner_deco_fletcher = cls.env.ref('base.res_partner_address_3')
        # Clear lines to make it more convenient to test it.
        cls.sale_1.order_line.unlink()
        cls.sale_1.write(
            {
                'client_order_ref': 'D123',
            }
        )

    def _assert_stamp_order_line(self, data, lines, description=None):
        product = data['product']
        line = lines.filtered(lambda r: r.product_id == product)
        self.assertEqual(len(line), 1)
        if description is None:
            description = product.description_sale
        self.assertEqual(line.name, description)
        self.assertEqual(line.product_uom_qty, data['quantity'])
        self.assertEqual(line.price_unit, data['price_unit'])

    def test_01_multi_stamp_configure_on_sale(self):
        # GIVEN
        ctx = self.sale_1.action_open_stamp_configurator()['context']
        # WHEN
        cfg_1 = self.StampConfigure.with_context(**ctx).create(
            {
                'die_id': self.stamp_die_default.id,
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
        res_1 = cfg_1.action_configure()
        # THEN
        self.assertEqual(cfg_1.partner_id, self.partner_deco)
        self.assertEqual(cfg_1.sequence, 1)
        self.assertEqual(cfg_1.sequence_counter_die, 1)
        self.assertEqual(cfg_1.origin, self.sale_1.name)
        self.assertEqual(cfg_1.ref, 'D123')
        order_lines = self.sale_1.order_line
        self.assertEqual(len(order_lines), 3)
        self._assert_stamp_order_line(res_1['die'], order_lines)
        self._assert_stamp_order_line(
            res_1['counter_die'],
            order_lines,
            description=res_1['counter_die']['product'].display_name,
        )
        self._assert_stamp_order_line(
            res_1['mold'],
            order_lines,
            description=res_1['mold']['product'].display_name,
        )
        # WHEN (configure again)
        cfg_2 = self.StampConfigure.with_context(**ctx).create(
            {
                'die_id': self.stamp_die_default.id,
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
                'quantity_mold': 0,
            }
        )
        cfg_2._onchange_design_id()
        res_2 = cfg_2.action_configure()
        # THEN
        self.assertEqual(cfg_2.partner_id, self.partner_deco)
        self.assertEqual(cfg_2.sequence, 2)
        self.assertEqual(cfg_2.sequence_counter_die, 1)
        self.assertEqual(cfg_2.origin, self.sale_1.name)
        self.assertEqual(cfg_2.ref, 'D123')
        order_lines = self.sale_1.order_line
        self.assertEqual(len(order_lines), 5)
        self._assert_stamp_order_line(res_2['die'], order_lines)
        self._assert_stamp_order_line(
            res_2['counter_die'],
            order_lines,
            description=res_2['counter_die']['product'].display_name,
        )

    def test_02_stamp_configure_sale_contact(self):
        # GIVEN
        ctx = self.sale_1.action_open_stamp_configurator()['context']
        self.sale_1.partner_id = self.partner_deco_fletcher.id
        cfg = self.StampConfigure.with_context(**ctx).create(
            {
                'die_id': self.stamp_die_default.id,
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
        self.assertEqual(cfg.partner_id, self.partner_deco)

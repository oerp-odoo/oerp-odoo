from odoo.addons.product_stamp_configurator.tests.common import (
    TestProductStampConfiguratorCommon,
)


class TestStampConfigureStock(TestProductStampConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_route_mto = cls.env.ref('stock.route_warehouse0_mto')
        cls.stock_route_mto.write(
            {
                'active': True,
                'product_selectable': True,
            }
        )
        cls.ResConfigSettings = cls.env['res.config.settings']

    def test_01_stamp_configure_use_default_stock(self):
        # GIVEN
        # Doing it via cfg settings to make sure option is set properly.
        res_cfg_settings = self.ResConfigSettings.create(
            {'stock_route_stamp_default_ids': [(6, 0, self.stock_route_mto.ids)]}
        )
        res_cfg_settings.execute()
        cfg = self.StampConfigure.create(
            {
                'partner_id': self.partner_azure.id,
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
        # WHEN
        res = cfg.action_configure()
        # THEN
        self.assertEqual(res['die']['product'].route_ids, self.stock_route_mto)
        self.assertEqual(
            res['counter_die']['product'].route_ids,
            self.stock_route_mto,
        )
        self.assertFalse(res['mold']['product'].route_ids)

    def test_02_stamp_configure_not_use_default_stock(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'partner_id': self.partner_azure.id,
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
        # WHEN
        res = cfg.action_configure()
        # THEN
        self.assertFalse(res['die']['product'].route_ids)
        self.assertFalse(res['counter_die']['product'].route_ids)
        self.assertFalse(res['mold']['product'].route_ids)

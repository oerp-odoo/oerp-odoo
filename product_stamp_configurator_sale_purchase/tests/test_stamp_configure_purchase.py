from odoo.exceptions import ValidationError

from odoo.addons.product_stamp_configurator.tests.common import (
    TestProductStampConfiguratorCommon,
)


class TestStampConfigurePurchase(TestProductStampConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResConfigSettings = cls.env['res.config.settings']

    def test_01_stamp_configure_use_service_to_purchase_without_vendor(self):
        with self.assertRaisesRegex(
            ValidationError,
            r"To use Service to Purchase for Stamp, you must also select Vendor!",
        ):
            self.ResConfigSettings.create({'service_to_purchase_stamp': True})

    def test_02_stamp_configure_use_default_purchase(self):
        # GIVEN
        self.company_main.service_to_purchase_stamp = True
        self.company_main.write(
            {
                'service_to_purchase_stamp': True,
                'partner_supplier_default_stamp_id': self.partner_azure.id,
            }
        )
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
                'margin_ratio': 1.2,
            }
        )
        # WHEN
        res = cfg.action_configure()
        # THEN
        self.assertEqual(cfg.price_unit_die, 39.0)
        self.assertEqual(cfg.price_unit_counter_die, 15.0)
        self.assertEqual(cfg.price_unit_mold, 0.0)
        self.assertEqual(cfg.cost_unit_die, 33.0)
        self.assertEqual(cfg.cost_unit_counter_die, 12.0)
        self.assertEqual(cfg.cost_unit_mold, 0.0)
        self.assertFalse(res['die']['product'].service_to_purchase)
        self.assertFalse(res['counter_die']['product'].service_to_purchase)
        self.assertTrue(res['mold']['product'].service_to_purchase)
        self.assertEqual(len(res['die']['product'].seller_ids), 1)
        self.assertEqual(len(res['counter_die']['product'].seller_ids), 1)
        self.assertEqual(len(res['mold']['product'].seller_ids), 1)
        self.assertEqual(res['die']['product'].seller_ids[0].price, 33.0)
        self.assertEqual(res['counter_die']['product'].seller_ids[0].price, 12.0)
        self.assertEqual(res['mold']['product'].seller_ids[0].price, 0.0)

    def test_03_stamp_configure_not_use_default_purchase(self):
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
        self.assertFalse(res['die']['product'].service_to_purchase)
        self.assertFalse(res['counter_die']['product'].service_to_purchase)
        self.assertFalse(res['mold']['product'].service_to_purchase)
        self.assertEqual(len(res['die']['product'].seller_ids), 0)
        self.assertEqual(len(res['counter_die']['product'].seller_ids), 0)
        self.assertEqual(len(res['mold']['product'].seller_ids), 0)

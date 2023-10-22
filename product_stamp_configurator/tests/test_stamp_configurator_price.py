from ..stamp.price import (
    calc_counter_die_price,
    calc_die_price,
    calc_discount_percent,
    calc_mold_price,
)
from .common import TestProductStampConfiguratorCommon


class TestStampConfiguratorPrice(TestProductStampConfiguratorCommon):
    def test_01_calc_die_price_f_b7_wo_finish_wo_emb_design(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 10,
                'quantity_spare_dies': 3,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
            }
        )
        # WHEN
        price = calc_die_price(cfg)
        # THEN
        self.assertEqual(price, 13.5)  # material price only
        # Sanity checks.
        self.assertEqual(cfg.quantity_dies_total, 13)
        self.assertEqual(cfg.quantity_counter_dies_total, 20)

    def test_02_calc_die_price_f_b7_w_finish_wo_emb_design(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'finishing_id': self.stamp_finishing_nickel.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 10,
                'quantity_spare_dies': 3,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
            }
        )
        # WHEN
        price = calc_die_price(cfg)
        # THEN
        # 13.5 (material price)
        # 24 (special finishing price)
        self.assertEqual(price, 37.5)

    def test_03_calc_die_price_f_b7_w_finish_w_emb_design(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_fe.id,
                'embossed_design_perc': 40.0,
                'material_id': self.stamp_material_brass_7.id,
                'finishing_id': self.stamp_finishing_nickel.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 10,
                'quantity_spare_dies': 3,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
            }
        )
        # WHEN
        price = calc_die_price(cfg)
        # THEN
        # 48.375 (difficulty coeff (0.75) * embossed design + material price)
        # 24 (special finishing price)
        self.assertEqual(price, 72.375)

    def test_04_calc_counter_die_price(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 4,
                'quantity_spare_dies': 1,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
            }
        )
        # WHEN
        price = calc_counter_die_price(cfg)
        # THEN
        # 150 * 0.08
        self.assertEqual(price, 12.0)

    def test_05_calc_mold_price_100_percent_of_die(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                # Deco has 100 percent of die price.
                'partner_id': self.partner_deco.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 1,
                'quantity_spare_dies': 1,
                'quantity_counter_dies': 1,
                'quantity_counter_spare_dies': 1,
            }
        )
        # WHEN
        price = calc_mold_price(cfg)
        # THEN
        self.assertEqual(price, 13.5)  # match die price
        self.assertEqual(calc_discount_percent(13.5, 13.5), 0)

    def test_06_calc_mold_price_50_percent_of_die(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                # Azure has 50 percent of die price.
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 1,
                'quantity_spare_dies': 1,
                'quantity_counter_dies': 1,
                'quantity_counter_spare_dies': 1,
            }
        )
        # WHEN
        price = calc_mold_price(cfg)
        # THEN
        self.assertEqual(price, 6.75)  # half of die price
        self.assertEqual(calc_discount_percent(13.5, 6.75), 50.0)

    def test_07_calc_mold_price_free_over_threshold(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_deco.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 4,
                'quantity_spare_dies': 1,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
            }
        )
        # WHEN
        price = calc_mold_price(cfg)
        # THEN
        self.assertEqual(price, 0.0)
        self.assertEqual(calc_discount_percent(13.5, 0.0), 100.0)

    def test_08_calc_die_price_under_minimum_area(self):
        # GIVEN
        # Minimum area is 200 and configurator uses 150.
        self.stamp_pricelist_azure.min_area = 200
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'finishing_id': self.stamp_finishing_nickel.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 10,
                'quantity_spare_dies': 3,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
            }
        )
        # WHEN
        price = calc_die_price(cfg)
        # THEN
        # 18.0 (material price)
        # 32.0 (special finishing price)
        self.assertEqual(price, 50.0)

    def test_09_calc_counter_die_price_under_minimum_area(self):
        # GIVEN
        self.stamp_pricelist_azure.min_area = 200
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 4,
                'quantity_spare_dies': 1,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
            }
        )
        # WHEN
        price = calc_counter_die_price(cfg)
        # THEN
        # 200 * 0.08
        self.assertEqual(price, 16.0)

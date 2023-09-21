from ..stamp.engraving import calc_engraving_time
from .common import TestProductStampConfiguratorCommon


class TestStampConfiguratorEngraving(TestProductStampConfiguratorCommon):
    def test_01_calc_engraving_time_die_f_b7_wo_emb_design(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
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
                'origin': '1111',
                'ref': '2222',
            }
        )
        # WHEN
        eng_time = calc_engraving_time(cfg)
        # THEN
        self.assertAlmostEqual(eng_time, 0.47, places=3)

    def test_02_calc_engraving_time_die_f_b7_w_emb_design(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_fe.id,
                'embossed_design_perc': 40.0,
                'material_id': self.stamp_material_brass_7.id,
                'material_counter_id': self.stamp_material_plastic_05.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 10,
                'quantity_spare_dies': 3,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
                'origin': '1111',
                'ref': '2222',
            }
        )
        # WHEN
        eng_time = calc_engraving_time(cfg)
        # THEN
        self.assertEqual(eng_time, 0.99)

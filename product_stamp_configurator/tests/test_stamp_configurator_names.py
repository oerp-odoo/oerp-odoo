from ..stamp.code import (
    generate_counter_die_code,
    generate_die_code,
    generate_mold_code,
)
from ..stamp.description import generate_die_description
from ..stamp.name import (
    generate_counter_die_name,
    generate_die_name,
    generate_mold_name,
)
from .common import TestProductStampConfiguratorCommon


class TestStampConfiguratorNames(TestProductStampConfiguratorCommon):
    def test_01_generate_names_die_f_b7_wo_finish(self):
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
                # Explicitly not specifying reference.
                'ref': False,
            }
        )
        # WHEN
        die_code = generate_die_code(cfg)
        mold_code = generate_mold_code(cfg)
        counter_die_code = generate_counter_die_code(cfg)
        die_name = generate_die_name(cfg)
        mold_name = generate_mold_name(cfg)
        counter_die_name = generate_counter_die_name(cfg)
        die_description = generate_die_description(cfg, 13.75)
        # THEN
        # origin+design.code+seq_code+material.code (ref is False, so omitted)
        self.assertEqual(die_code, '1111F1B7')
        self.assertEqual(mold_code, '1111F1P1')
        self.assertEqual(counter_die_code, '1111F1P1P0.5')
        self.assertEqual(die_name, 'Brass Die, HFS, F1, 7 mm+ Spare 3 pcs')
        self.assertEqual(mold_name, 'Molding service F1')
        self.assertEqual(
            counter_die_name, 'Plastic Counter-Die, F1, 0.5 mm+ Spare 10 pcs'
        )
        self.assertEqual(die_description, '15x10 cm ; A ; 0.09 eur/cm ; 0.5 val')

    def test_02_generate_names_die_f_b7_w_finish(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 2,
                'sequence_counter_die': 2,
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'finishing_id': self.stamp_finishing_nickel.id,
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
        die_code = generate_die_code(cfg)
        mold_code = generate_mold_code(cfg)
        counter_die_code = generate_counter_die_code(cfg)
        # THEN
        # origin+design.code+seq_code+material.code+finishing.code+ref
        self.assertEqual(die_code, '1111F2B7N / 2222')
        self.assertEqual(mold_code, '1111F2P2 / 2222')
        self.assertEqual(counter_die_code, '1111F2P2P0.5 / 2222')

    def test_03_generate_names_insert_die_f_b7_w_finish_w_emb_design(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 3,
                'sequence_counter_die': 3,
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_insert.id,
                'insert_die_ref': 'FE2',
                'design_id': self.stamp_design_fe.id,
                'embossed_design_perc': 40.0,
                'material_id': self.stamp_material_brass_7.id,
                'finishing_id': self.stamp_finishing_nickel.id,
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
        die_code = generate_die_code(cfg)
        mold_code = generate_mold_code(cfg)
        counter_die_code = generate_counter_die_code(cfg)
        die_name = generate_die_name(cfg)
        mold_name = generate_mold_name(cfg)
        counter_die_name = generate_counter_die_name(cfg)
        die_description = generate_die_description(cfg, 72.375)
        # THEN
        # origin+die.code+design.code+seq_code+material.code+ref
        self.assertEqual(die_code, '1111FE2iFE3B7N / 2222')
        self.assertEqual(mold_code, '1111FE2iFE3P3 / 2222')
        self.assertEqual(counter_die_code, '1111FE2iFE3P3P0.5 / 2222')
        self.assertEqual(
            die_name, 'Brass Insert Die, Foil + Emboss, FE3, 7 mm+ Spare 3 pcs'
        )
        self.assertEqual(mold_name, 'Molding service iFE3')
        self.assertEqual(
            counter_die_name, 'Plastic Counter-Die, iFE3, 0.5 mm+ Spare 10 pcs'
        )
        self.assertEqual(die_description, '15x10 cm ; A ; 0.48 eur/cm ; 1 val')

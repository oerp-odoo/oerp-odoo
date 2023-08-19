from .common import TestProductStampConfiguratorCommon


class TestStampConfigure(TestProductStampConfiguratorCommon):
    def test_01_stamp_configure_die_with_counter_die_and_mold(self):
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
                'quantity_mold': 1,
                'origin': '1111',
                'ref': '2222',
            }
        )
        # WHEN
        res = cfg.action_configure()
        # THEN
        self.assertEqual(cfg.category_counter_die_id, self.product_categ_furniture)
        self.assertEqual(cfg.category_mold_id, self.product_categ_service)
        self.assertEqual(len(res), 3)
        # Die
        self.assertEqual(res['die']['quantity'], 13)
        self.assertEqual(res['die']['price_unit'], 13.5)
        product_die = res['die']['product']
        self.assertEqual(product_die.type, 'consu')
        self.assertEqual(product_die.default_code, '1111F1B7 / 2222')
        self.assertEqual(product_die.name, 'Brass Die, HFS, F1, 7 mm+ Spare 3 pcs')
        self.assertEqual(
            product_die.description_sale, '15x10 cm ; A ; 0.09 eur/cm ; 0.5 val'
        )
        self.assertEqual(product_die.categ_id, self.product_categ_consu)
        # Counter Die
        self.assertEqual(res['counter_die']['quantity'], 20)
        self.assertEqual(res['counter_die']['price_unit'], 12)
        product_counter_die = res['counter_die']['product']
        self.assertEqual(product_counter_die.type, 'consu')
        self.assertEqual(product_counter_die.default_code, '1111F1P1P0.5 / 2222')
        self.assertEqual(
            product_counter_die.name, 'Plastic Counter-Die, F1, 0.5 mm+ Spare 10 pcs'
        )
        self.assertFalse(product_counter_die.description_sale)
        self.assertEqual(product_counter_die.categ_id, self.product_categ_furniture)
        # Mold
        self.assertEqual(res['mold']['quantity'], 1)
        self.assertEqual(res['mold']['price_unit'], 0.0)
        product_mold = res['mold']['product']
        self.assertEqual(product_mold.type, 'service')
        self.assertEqual(product_mold.default_code, '1111F1P1 / 2222')
        self.assertEqual(product_mold.name, 'Molding service F1')
        self.assertFalse(product_mold.description_sale)
        self.assertEqual(product_mold.categ_id, self.product_categ_service)

    def test_02_stamp_configure_die_without_counter_die_and_mold(self):
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
                'quantity_counter_dies': 0,
                'quantity_counter_spare_dies': 0,
                'quantity_mold': 0,
                'origin': '1111',
                'ref': '2222',
            }
        )
        # WHEN
        res = cfg.action_configure()
        # THEN
        self.assertEqual(cfg.category_counter_die_id, self.product_categ_furniture)
        self.assertEqual(cfg.category_mold_id, self.product_categ_service)
        self.assertEqual(len(res), 1)
        # Die
        self.assertEqual(res['die']['quantity'], 13)
        self.assertEqual(res['die']['price_unit'], 13.5)
        product_die = res['die']['product']
        self.assertEqual(product_die.type, 'consu')
        self.assertEqual(product_die.default_code, '1111F1B7 / 2222')
        self.assertEqual(product_die.name, 'Brass Die, HFS, F1, 7 mm+ Spare 3 pcs')
        self.assertEqual(
            product_die.description_sale, '15x10 cm ; A ; 0.09 eur/cm ; 0.5 val'
        )

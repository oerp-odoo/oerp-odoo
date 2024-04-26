from odoo.exceptions import ValidationError

from .common import TestProductStampConfiguratorCommon


class TestStampConfigure(TestProductStampConfiguratorCommon):
    def test_01_stamp_configure_die_with_counter_die_and_mold(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                # die_id omitted, expecting to use default from settings.
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
                'quantity_mold': 1,
            }
        )
        # WHEN
        res = cfg.action_configure()
        # THEN
        # Prices on configurator itself.
        self.assertEqual(cfg.price_sqcm_die_suggested, 0.22)
        self.assertEqual(cfg.price_sqcm_counter_die_suggested, 0.08)
        self.assertEqual(cfg.price_sqcm_mold_suggested, 0.0)
        self.assertEqual(cfg.price_sqcm_die_custom, 0.0)
        self.assertEqual(cfg.price_sqcm_counter_die_custom, 0.0)
        self.assertEqual(cfg.price_sqcm_mold_custom, 0.0)
        self.assertEqual(cfg.price_unit_die, 33.0)
        self.assertEqual(cfg.price_unit_counter_die, 12.0)
        self.assertEqual(cfg.price_unit_mold, 0.0)
        self.assertEqual(cfg.cost_unit_die, 33.0)
        self.assertEqual(cfg.cost_unit_counter_die, 12.0)
        self.assertEqual(cfg.cost_unit_mold, 0.0)
        # Other asserts.
        self.assertEqual(cfg.category_counter_die_id, self.product_categ_furniture)
        self.assertEqual(cfg.category_mold_id, self.product_categ_service)
        self.assertEqual(len(res), 3)
        # Die
        self.assertEqual(res['die']['quantity'], 13)
        self.assertEqual(res['die']['price_unit'], 33.0)
        product_die = res['die']['product']
        self.assertEqual(product_die.company_id, self.company_main)
        self.assertEqual(product_die.stamp_type, 'die')
        self.assertFalse(product_die.is_insert_die)
        self.assertEqual(product_die.weight, 315.0)
        self.assertEqual(product_die.type, 'consu')
        self.assertEqual(product_die.default_code, '1111F1B7 / 2222')
        self.assertEqual(product_die.name, 'Brass Die, HFS, F1, 7 mm+ Spare 3 pcs')
        self.assertEqual(
            product_die.description_sale, '15x10 cm ; A ; 0.22 eur/cm ; 0.5 val'
        )
        self.assertEqual(product_die.categ_id, self.product_categ_consu)
        # Counter Die
        self.assertEqual(res['counter_die']['quantity'], 20)
        self.assertEqual(res['counter_die']['price_unit'], 12)
        product_counter_die = res['counter_die']['product']
        self.assertEqual(product_counter_die.company_id, self.company_main)
        self.assertEqual(product_counter_die.stamp_type, 'counter_die')
        self.assertFalse(product_counter_die.is_insert_die)
        self.assertEqual(product_counter_die.weight, 135.0)
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
        self.assertEqual(product_mold.company_id, self.company_main)
        self.assertEqual(product_mold.stamp_type, 'mold')
        self.assertFalse(product_mold.is_insert_die)
        self.assertEqual(product_die.weight, 315.0)
        self.assertEqual(product_mold.type, 'service')
        self.assertEqual(product_mold.default_code, '1111F1P1 / 2222')
        self.assertEqual(product_mold.name, 'Molding service F1')
        self.assertFalse(product_mold.description_sale)
        self.assertEqual(product_mold.categ_id, self.product_categ_service)
        self.assertFalse(cfg.is_insert_die)
        # WHEN
        on_res = cfg._onchange_die_id()
        # THEN
        self.assertEqual(
            on_res, {'domain': {'product_insert_die_ref_id': [(1, '=', 1)]}}
        )
        for product in product_die | product_counter_die | product_mold:
            # Expect new message to be added with configurator parameters.
            msg = product.message_ids[0]
            self.assertIn(
                'size_length', msg.body, f'Product: {product.name}. Message: {msg.body}'
            )
            tmpl = product.product_tmpl_id
            msg = tmpl.message_ids[0]
            self.assertIn(
                'size_length',
                msg.body,
                f'Product Template: {tmpl.name}. Message: {msg.body}',
            )

    def test_02_stamp_configure_insert_die_without_counter_die_and_mold(self):
        # GIVEN
        product_ref = self.ProductProduct.create(
            {
                'name': 'Die Ref 1',
                'default_code': '1111F1B7 / 2222',
                'stamp_type': 'die',
            }
        )
        cfg = self.StampConfigure.create(
            {
                'sequence': 2,
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_insert.id,
                'product_insert_die_ref_id': product_ref.id,
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
        self.assertEqual(cfg.insert_die_ref, 'F1')
        self.assertEqual(cfg.category_counter_die_id, self.product_categ_furniture)
        self.assertEqual(cfg.category_mold_id, self.product_categ_service)
        self.assertEqual(len(res), 1)
        # Die
        self.assertEqual(res['die']['quantity'], 13)
        self.assertEqual(res['die']['price_unit'], 33.0)
        product_die = res['die']['product']
        self.assertEqual(product_die.stamp_type, 'die')
        self.assertTrue(product_die.is_insert_die)
        self.assertEqual(product_die.weight, 315.0)
        self.assertEqual(product_die.type, 'consu')
        self.assertEqual(product_die.default_code, '1111F1iF2B7 / 2222')
        self.assertEqual(
            product_die.name, 'Brass Insert Die, HFS, F2, 7 mm+ Spare 3 pcs'
        )
        self.assertEqual(
            product_die.description_sale, '15x10 cm ; A ; 0.22 eur/cm ; 0.5 val'
        )
        self.assertTrue(cfg.is_insert_die)
        # WHEN
        on_res = cfg._onchange_die_id()
        # THEN
        self.assertEqual(
            on_res,
            {
                'domain': {
                    'product_insert_die_ref_id': [
                        ('stamp_type', '=', 'die'),
                        ('is_insert_die', '=', False),
                    ]
                }
            },
        )

    def test_03_stamp_configure_categories_missing_or_wrong_stamp_type(self):
        # GIVEN.
        # No type for die category.
        self.product_categ_consu.stamp_type = False
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
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Die must have Category \(.+\) with Die type!"
        ):
            cfg.action_configure()
        # GIVEN
        self.product_categ_consu.stamp_type = 'die'
        # Set wrong type for counter die categ.
        self.product_categ_furniture.stamp_type = 'mold'
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"Counter Die must have Category \(.+\) with Counter Die type!",
        ):
            cfg.action_configure()
        # GIVEN
        self.product_categ_furniture.stamp_type = 'counter_die'
        self.product_categ_service.stamp_type = False
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Mold must have Category \(.+\) with Mold type!"
        ):
            cfg.action_configure()

    def test_04_stamp_configure_default_mold_quantity(self):
        # GIVEN
        # To use quantity_mold default on design onchange.
        self.stamp_design_f.is_embossed = True
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                # die_id omitted, expecting to use default from settings.
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
        cfg._onchange_design()
        # THEN
        self.assertEqual(cfg.quantity_mold, 1)

    def test_05_stamp_configure_without_counter_die_category(self):
        # GIVEN
        self.company_main.category_default_counter_die_id = False
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                # die_id omitted, expecting to use default from settings.
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
                'quantity_mold': 1,
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"Counter Die Category is missing for your stamp type \(counter_die\)",
        ):
            cfg.action_configure()

    def test_06_stamp_configure_without_mold_category(self):
        # GIVEN
        self.company_main.category_default_mold_id = False
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                # die_id omitted, expecting to use default from settings.
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
                'quantity_mold': 1,
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Mold Category is missing for your stamp type \(mold\)"
        ):
            cfg.action_configure()

    def test_07_stamp_configure_onchange_die_quantity_is_not_embossed(self):
        # GIVEN
        self.stamp_design_f.is_embossed = False
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
                'origin': '1111',
                'ref': '2222',
            }
        )
        # WHEN
        cfg._onchange_quantity_dies()
        # THEN
        self.assertEqual(cfg.quantity_counter_dies, 0)

    def test_08_stamp_configure_onchange_die_quantity_is_embossed(self):
        # GIVEN
        self.stamp_design_f.is_embossed = True
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
                'origin': '1111',
                'ref': '2222',
            }
        )
        # WHEN
        cfg._onchange_quantity_dies()
        # THEN
        self.assertEqual(cfg.quantity_counter_dies, 10)

    def test_09_stamp_configure_shared_products(self):
        # GIVEN
        self.company_main.stamp_products_shared = True
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
                'quantity_counter_dies': 5,
                'quantity_mold': 1,
                'origin': '1111',
                'ref': '2222',
            }
        )
        # WHEN
        res = cfg.action_configure()
        # THEN
        self.assertFalse(res['die']['product'].company_id)
        self.assertFalse(res['counter_die']['product'].company_id)
        self.assertFalse(res['mold']['product'].company_id)

    def test_10_stamp_configure_die_with_counter_die_and_mold_custom_prices(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                # die_id omitted, expecting to use default from settings.
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
                'quantity_mold': 1,
                'price_sqcm_die_custom': 0.1,
                'price_sqcm_counter_die_custom': 0.2,
                'price_sqcm_mold_custom': 0.3,
            }
        )
        # WHEN
        res = cfg.action_configure()
        # THEN
        # Prices on configurator itself.
        self.assertEqual(cfg.price_sqcm_die_suggested, 0.22)
        self.assertEqual(cfg.price_sqcm_counter_die_suggested, 0.08)
        self.assertEqual(cfg.price_sqcm_mold_suggested, 0.0)
        self.assertEqual(cfg.price_sqcm_die_custom, 0.1)
        self.assertEqual(cfg.price_sqcm_counter_die_custom, 0.2)
        self.assertEqual(cfg.price_sqcm_mold_custom, 0.3)
        self.assertEqual(cfg.price_unit_die, 15.0)
        self.assertEqual(cfg.price_unit_counter_die, 30.0)
        self.assertEqual(cfg.price_unit_mold, 45.0)
        self.assertEqual(cfg.cost_unit_die, 15.0)
        self.assertEqual(cfg.cost_unit_counter_die, 30.0)
        self.assertEqual(cfg.cost_unit_mold, 45.0)
        # Other asserts.
        self.assertEqual(cfg.category_counter_die_id, self.product_categ_furniture)
        self.assertEqual(cfg.category_mold_id, self.product_categ_service)
        self.assertEqual(len(res), 3)
        # Die
        self.assertEqual(res['die']['quantity'], 13)
        self.assertEqual(res['die']['price_unit'], 15.0)
        product_die = res['die']['product']
        self.assertEqual(product_die.company_id, self.company_main)
        self.assertEqual(product_die.stamp_type, 'die')
        self.assertFalse(product_die.is_insert_die)
        self.assertEqual(product_die.weight, 315.0)
        self.assertEqual(product_die.type, 'consu')
        self.assertEqual(product_die.default_code, '1111F1B7 / 2222')
        self.assertEqual(product_die.name, 'Brass Die, HFS, F1, 7 mm+ Spare 3 pcs')
        self.assertEqual(
            product_die.description_sale, '15x10 cm ; A ; 0.10 eur/cm ; 0.5 val'
        )
        self.assertEqual(product_die.categ_id, self.product_categ_consu)
        # Counter Die
        self.assertEqual(res['counter_die']['quantity'], 20)
        self.assertEqual(res['counter_die']['price_unit'], 30.0)
        product_counter_die = res['counter_die']['product']
        self.assertEqual(product_counter_die.company_id, self.company_main)
        self.assertEqual(product_counter_die.stamp_type, 'counter_die')
        self.assertFalse(product_counter_die.is_insert_die)
        self.assertEqual(product_counter_die.weight, 135.0)
        self.assertEqual(product_counter_die.type, 'consu')
        self.assertEqual(product_counter_die.default_code, '1111F1P1P0.5 / 2222')
        self.assertEqual(
            product_counter_die.name, 'Plastic Counter-Die, F1, 0.5 mm+ Spare 10 pcs'
        )
        self.assertFalse(product_counter_die.description_sale)
        self.assertEqual(product_counter_die.categ_id, self.product_categ_furniture)
        # Mold
        self.assertEqual(res['mold']['quantity'], 1)
        self.assertEqual(res['mold']['price_unit'], 45.0)
        product_mold = res['mold']['product']
        self.assertEqual(product_mold.company_id, self.company_main)
        self.assertEqual(product_mold.stamp_type, 'mold')
        self.assertFalse(product_mold.is_insert_die)
        self.assertEqual(product_die.weight, 315.0)
        self.assertEqual(product_mold.type, 'service')
        self.assertEqual(product_mold.default_code, '1111F1P1 / 2222')
        self.assertEqual(product_mold.name, 'Molding service F1')
        self.assertFalse(product_mold.description_sale)
        self.assertEqual(product_mold.categ_id, self.product_categ_service)
        self.assertFalse(cfg.is_insert_die)

    def test_11_stamp_price_cost_with_margin(self):
        # GIVEN, WHEN
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                # die_id omitted, expecting to use default from settings.
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
                'quantity_mold': 1,
                'price_sqcm_die_custom': 0.1,
                'price_sqcm_counter_die_custom': 0.2,
                'price_sqcm_mold_custom': 0.3,
                # To make price higher than cost.
                'margin_ratio': 1.2,
            }
        )
        # THEN
        # Prices on configurator itself.
        self.assertEqual(cfg.price_sqcm_die_suggested, 0.26)
        self.assertEqual(cfg.price_sqcm_counter_die_suggested, 0.1)
        self.assertEqual(cfg.price_sqcm_mold_suggested, 0.0)
        self.assertEqual(cfg.price_sqcm_die_custom, 0.1)
        self.assertEqual(cfg.price_sqcm_counter_die_custom, 0.2)
        self.assertEqual(cfg.price_sqcm_mold_custom, 0.3)
        self.assertEqual(cfg.price_unit_die, 18.0)
        self.assertEqual(cfg.price_unit_counter_die, 36.0)
        self.assertEqual(cfg.price_unit_mold, 54.0)
        self.assertEqual(cfg.cost_unit_die, 15.0)
        self.assertEqual(cfg.cost_unit_counter_die, 30.0)
        self.assertEqual(cfg.cost_unit_mold, 45.0)

    def test_12_stamp_configure_die_translated_products(self):
        # GIVEN
        self.stamp_die_default.update_field_translations('name', {'lt_LT': 'Klišė'})
        self.stamp_design_f.update_field_translations('name', {'lt_LT': 'HFS_LT'})
        self.material_label_brass.update_field_translations(
            'name', {'lt_LT': 'Žalvario'}
        )
        self.material_label_plastic.update_field_translations(
            'name', {'lt_LT': 'Plastiko'}
        )
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                # die_id omitted, expecting to use default from settings.
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
                'quantity_mold': 1,
            }
        )
        # WHEN
        res = cfg.action_configure()
        # THEN
        # Prices on configurator itself.
        # Other asserts.
        self.assertEqual(cfg.category_counter_die_id, self.product_categ_furniture)
        self.assertEqual(cfg.category_mold_id, self.product_categ_service)
        self.assertEqual(len(res), 3)
        # Die
        product_die = res['die']['product']
        self.assertEqual(product_die.name, 'Brass Die, HFS, F1, 7 mm+ Spare 3 pcs')
        self.assertEqual(
            product_die.with_context(lang='lt_LT').name,
            'Žalvario Klišė, HFS_LT, F1, 7 mm+ Atsarginė(-s) 3 dalis(-ys)',
        )
        # Counter Die
        product_counter_die = res['counter_die']['product']
        self.assertEqual(
            product_counter_die.name, 'Plastic Counter-Die, F1, 0.5 mm+ Spare 10 pcs'
        )
        self.assertEqual(
            product_counter_die.with_context(lang='lt_LT').name,
            'Plastiko Patrica, F1, 0.5 mm+ Atsarginė(-s) 10 dalis(-ys)',
        )
        # Mold
        product_mold = res['mold']['product']
        self.assertEqual(product_mold.name, 'Molding service F1')
        self.assertEqual(
            product_mold.with_context(lang='lt_LT').name, 'Liejimo paslauga F1'
        )

    def test_13_stamp_configure_pricelist_margin_ratio(self):
        # GIVEN
        self.stamp_pricelist_azure.margin_default_ratio = 1.5
        cfg = self.StampConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                # die_id omitted, expecting to use default from settings.
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
                'quantity_mold': 1,
                'price_sqcm_die_custom': 0.1,
                'price_sqcm_counter_die_custom': 0.2,
                'price_sqcm_mold_custom': 0.3,
                # To make price higher than cost.
                'margin_ratio': 1.2,
            }
        )
        # WHEN
        cfg._onchange_partner_id()
        # THEN
        self.assertEqual(cfg.margin_ratio, 1.5)

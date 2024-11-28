from . import common


class TestPackageBoxSetupRuleQty(common.TestProductPackageConfiguratorCommon):
    def test_01_box_setup_rule_qty_fixed(self):
        # GIVEN
        setup_1 = self.PackageBoxSetup.create(
            {
                'name': 'MY-BOX-SHEET-SETUP-1',
                'setup_type': 'sheet',
                'setup_qty_mode': 'fixed',
            }
        )
        rules = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 2000, 'setup_qty': 200},
                {'setup_id': setup_1.id, 'min_qty': 1000, 'setup_qty': 100},
            ]
        )
        setup_1_rule_1 = rules[0]
        setup_1_rule_2 = rules[1]
        # WHEN min_qty is bare minimum
        qty = setup_1_rule_2.calc_setup_qty(1000)
        # THEN
        self.assertEqual(qty, 100)
        # WHEN min_qty is bare between two rules
        qty = setup_1_rule_2.calc_setup_qty(1400)
        # THEN
        self.assertEqual(qty, 100)
        # WHEN min_qty is bare minimum on first rule
        qty = setup_1_rule_1.calc_setup_qty(2000)
        # THEN
        self.assertEqual(qty, 200)
        # WHEN min_qty is over bare minimum on first rule
        qty = setup_1_rule_1.calc_setup_qty(5000)
        # THEN
        self.assertEqual(qty, 200)

    def test_02_box_setup_rule_qty_rel(self):
        # GIVEN
        setup_1 = self.PackageBoxSetup.create(
            {
                'name': 'MY-BOX-SHEET-SETUP-1',
                'setup_type': 'sheet',
                'setup_qty_mode': 'relative',
            }
        )
        rules = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 2000, 'setup_qty': 200},
                {'setup_id': setup_1.id, 'min_qty': 1000, 'setup_qty': 100},
            ]
        )
        setup_1_rule_1 = rules[0]
        setup_1_rule_2 = rules[1]
        # WHEN min_qty is bare minimum
        qty = setup_1_rule_2.calc_setup_qty(1000)
        # THEN
        self.assertEqual(qty, 100)
        # WHEN min_qty is bare between two rules
        qty = setup_1_rule_2.calc_setup_qty(1400)
        # THEN
        self.assertEqual(qty, 140)
        # WHEN min_qty is bare minimum on first rule
        qty = setup_1_rule_1.calc_setup_qty(2000)
        # THEN
        self.assertEqual(qty, 200)
        # WHEN min_qty is over bare minimum on first rule
        qty = setup_1_rule_1.calc_setup_qty(5000)
        # THEN
        self.assertEqual(qty, 200)

    def test_03_box_setup_rule_qty_rel_uneven(self):
        # GIVEN
        setup_1 = self.PackageBoxSetup.create(
            {
                'name': 'MY-BOX-SHEET-SETUP-1',
                'setup_type': 'sheet',
                'setup_qty_mode': 'relative',
            }
        )
        rules = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1700, 'setup_qty': 251},
                {'setup_id': setup_1.id, 'min_qty': 1000, 'setup_qty': 90},
            ]
        )
        setup_1_rule_1 = rules[0]
        setup_1_rule_2 = rules[1]
        # WHEN min_qty is bare minimum
        qty = setup_1_rule_2.calc_setup_qty(1000)
        # THEN
        self.assertEqual(qty, 90)
        # WHEN min_qty is bare between two rules
        qty = setup_1_rule_2.calc_setup_qty(1401)
        # THEN
        # It is ceiled up!
        self.assertEqual(qty, 183)
        # WHEN min_qty is bare minimum on first rule
        qty = setup_1_rule_1.calc_setup_qty(1700)
        # THEN
        self.assertEqual(qty, 251)
        # WHEN min_qty is over bare minimum on first rule
        qty = setup_1_rule_1.calc_setup_qty(5000)
        # THEN
        self.assertEqual(qty, 251)

    def test_04_box_setup_rule_qty_rel_invalid(self):
        # GIVEN
        setup_1 = self.PackageBoxSetup.create(
            {
                'name': 'MY-BOX-SHEET-SETUP-1',
                'setup_type': 'sheet',
                'setup_qty_mode': 'relative',
            }
        )
        rules = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 2000, 'setup_qty': 200},
                {'setup_id': setup_1.id, 'min_qty': 1000, 'setup_qty': 100},
            ]
        )
        setup_1_rule_2 = rules[1]
        # WHEN min_qty is below bare minimum
        qty = setup_1_rule_2.calc_setup_qty(500)
        # THEN
        self.assertEqual(qty, 100)
        # WHEN min_qty is over max.
        qty = setup_1_rule_2.calc_setup_qty(5000)
        # THEN
        self.assertEqual(qty, 200)

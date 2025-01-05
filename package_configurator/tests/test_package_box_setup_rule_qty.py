from . import common


class TestPackageBoxSetupRuleQty(common.TestProductPackageConfiguratorCommon):
    def test_01_package_setup_rule_qty_fixed(self):
        # GIVEN
        setup_1 = self.PackageBoxSetup.create(
            {
                'name': 'MY-BOX-PRODUCTION-SETUP-1',
                'setup_type': 'production',
                'setup_qty_mode': 'fixed',
            }
        )
        rules = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 2000, 'setup_fixed_qty': 200},
                {'setup_id': setup_1.id, 'min_qty': 1000, 'setup_fixed_qty': 100},
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

    def test_02_package_setup_rule_qty_rel(self):
        # GIVEN
        setup_1 = self.PackageBoxSetup.create(
            {
                'name': 'MY-BOX-PRODUCTION-SETUP-1',
                'setup_type': 'production',
                'setup_qty_mode': 'relative',
            }
        )
        rules = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 2000, 'setup_fixed_qty': 200},
                {'setup_id': setup_1.id, 'min_qty': 1000, 'setup_fixed_qty': 100},
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

    def test_03_package_setup_rule_qty_rel_uneven(self):
        # GIVEN
        setup_1 = self.PackageBoxSetup.create(
            {
                'name': 'MY-BOX-PRODUCTION-SETUP-1',
                'setup_type': 'production',
                'setup_qty_mode': 'relative',
            }
        )
        rules = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1700, 'setup_fixed_qty': 251},
                {'setup_id': setup_1.id, 'min_qty': 1000, 'setup_fixed_qty': 90},
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

    def test_04_package_setup_rule_qty_rel_invalid(self):
        # GIVEN
        setup_1 = self.PackageBoxSetup.create(
            {
                'name': 'MY-BOX-PRODUCTION-SETUP-1',
                'setup_type': 'production',
                'setup_qty_mode': 'relative',
            }
        )
        rules = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 2000, 'setup_fixed_qty': 200},
                {'setup_id': setup_1.id, 'min_qty': 1000, 'setup_fixed_qty': 100},
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

    # TODO: create TestPackageBoxSetupRule class and move these tests.
    def test_05_package_setup_inp_qty_measure_component(self):
        # GIVEN
        setup = self.PackageBoxSetup.create(
            {
                'name': 'MY-BOX-PRODUCTION-SETUP-1',
                'setup_type': 'production',
                'inp_qty_measure': 'component',
            }
        )
        # WHEN
        inp_qty = setup.convert_inp_qty(200, 27)
        # THEN
        self.assertEqual(inp_qty, 200)

    def test_06_package_setup_inp_qty_measure_raw(self):
        # GIVEN
        setup = self.PackageBoxSetup.create(
            {
                'name': 'MY-BOX-PRODUCTION-SETUP-1',
                'setup_type': 'production',
                # Raw Sheets
                'inp_qty_measure': 'raw_sheet',
            }
        )
        # WHEN
        inp_qty = setup.convert_inp_qty(200, 27)
        # THEN
        self.assertEqual(inp_qty, 8)

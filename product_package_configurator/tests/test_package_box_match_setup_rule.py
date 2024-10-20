from ..value_objects.layout import Layout2D
from . import common


class TestPackageBoxMatchSetupRule(common.TestProductPackageConfiguratorCommon):
    def test_01_match_setup_rule_by_box_qty_setup_order_one(self):
        # GIVEN
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': 'sheet',
                },
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': 'sheet',
                },
            ],
        )
        rules = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 100, 'setup_qty': 0},
                {'setup_id': setup_1.id, 'min_qty': 200, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 300, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 400, 'setup_qty': 0},
            ]
        )
        setup_1_rule_1 = rules[0]
        setup_1_rule_2 = rules[1]
        # WHEN QTY too low for any rule
        rule = (setup_1 | setup_2).match_setup_rule(50)
        # THEN
        self.assertEqual(rule, self.PackageBoxSetupRule)
        # WHEN QTY less than 200
        rule = (setup_1 | setup_2).match_setup_rule(150)
        # THEN
        self.assertEqual(rule, setup_1_rule_1)
        # WHEN QTY less than 300
        rule = (setup_1 | setup_2).match_setup_rule(250)
        # THEN
        self.assertEqual(rule, setup_1_rule_2)
        # WHEN QTY is 300
        rule = (setup_1 | setup_2).match_setup_rule(300)
        # THEN
        self.assertEqual(rule, setup_1_rule_2)
        # WHEN QTY less than 400
        rule = (setup_1 | setup_2).match_setup_rule(350)
        # THEN
        self.assertEqual(rule, setup_1_rule_2)
        # WHEN QTY greater than 400
        rule = (setup_1 | setup_2).match_setup_rule(450)
        # THEN
        self.assertEqual(rule, setup_1_rule_2)

    def test_02_match_setup_rule_by_box_qty_setup_order_two(self):
        # GIVEN
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': 'sheet',
                },
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': 'sheet',
                },
            ],
        )
        (
            setup_1_rule_1,
            setup_1_rule_2,
            setup_2_rule_1,
            setup_2_rule_2,
        ) = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 100, 'setup_qty': 0},
                {'setup_id': setup_1.id, 'min_qty': 200, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 300, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 400, 'setup_qty': 0},
            ]
        )
        layout = Layout2D(length=100, width=50)
        # WHEN QTY too low for any rule
        rule = (setup_2 | setup_1).match_setup_rule(50, layout)
        # THEN
        self.assertEqual(rule, self.PackageBoxSetupRule)
        # WHEN QTY less than 200
        rule = (setup_2 | setup_1).match_setup_rule(150, layout)
        # THEN
        self.assertEqual(rule, setup_1_rule_1)
        # WHEN QTY less than 300
        rule = (setup_2 | setup_1).match_setup_rule(250, layout)
        # THEN
        self.assertEqual(rule, setup_1_rule_2)
        # WHEN QTY is 300
        rule = (setup_2 | setup_1).match_setup_rule(300, layout)
        # THEN
        self.assertEqual(rule, setup_2_rule_1)
        # WHEN QTY less than 400
        rule = (setup_2 | setup_1).match_setup_rule(350, layout)
        # THEN
        self.assertEqual(rule, setup_2_rule_1)
        # WHEN QTY greater than 400
        rule = (setup_2 | setup_1).match_setup_rule(450, layout)
        # THEN
        self.assertEqual(rule, setup_2_rule_2)

    def test_03_match_setup_rule_by_min_layout_length(self):
        # GIVEN
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': 'sheet',
                    'min_layout_length': 200,
                },
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': 'sheet',
                    'min_layout_length': 100,
                },
            ],
        )
        setup_1_rule_1, setup_2_rule_1 = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 1, 'setup_qty': 0},
            ]
        )
        # WHEN layout length less than 100
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=50, width=50))
        # THEN
        self.assertEqual(rule, self.PackageBoxSetupRule)
        # WHEN layout length less than 200
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=150, width=50))
        # THEN
        self.assertEqual(rule, setup_2_rule_1)
        # WHEN layout length greater than 200
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=250, width=50))
        # THEN
        self.assertEqual(rule, setup_1_rule_1)

    def test_04_match_setup_rule_by_max_layout_length(self):
        # GIVEN
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': 'sheet',
                    'max_layout_length': 200,
                },
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': 'sheet',
                    'max_layout_length': 100,
                },
            ],
        )
        setup_1_rule_1, setup_2_rule_1 = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 1, 'setup_qty': 0},
            ]
        )
        # WHEN layout length less than 100
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=50, width=50))
        # THEN
        self.assertEqual(rule, setup_1_rule_1)
        # WHEN layout length less than 200
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=150, width=50))
        # THEN
        self.assertEqual(rule, setup_1_rule_1)
        # WHEN layout length greater than 200
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=250, width=50))
        # THEN
        self.assertEqual(rule, self.PackageBoxSetupRule)

    def test_05_match_setup_rule_by_min_layout_width(self):
        # GIVEN
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': 'sheet',
                    'min_layout_width': 200,
                },
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': 'sheet',
                    'min_layout_width': 100,
                },
            ],
        )
        setup_1_rule_1, setup_2_rule_1 = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 1, 'setup_qty': 0},
            ]
        )
        # WHEN layout width less than 100
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=50, width=50))
        # THEN
        self.assertEqual(rule, self.PackageBoxSetupRule)
        # WHEN layout width less than 200
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=50, width=150))
        # THEN
        self.assertEqual(rule, setup_2_rule_1)
        # WHEN layout width greater than 200
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=50, width=250))
        # THEN
        self.assertEqual(rule, setup_1_rule_1)

    def test_06_match_setup_rule_by_max_layout_width(self):
        # GIVEN
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': 'sheet',
                    'max_layout_width': 200,
                },
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': 'sheet',
                    'max_layout_width': 100,
                },
            ],
        )
        setup_1_rule_1, _setup_2_rule_1 = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 1, 'setup_qty': 0},
            ]
        )
        # WHEN layout width less than 100
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=50, width=50))
        # THEN
        self.assertEqual(rule, setup_1_rule_1)
        # WHEN layout width less than 200
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=50, width=150))
        # THEN
        self.assertEqual(rule, setup_1_rule_1)
        # WHEN layout width greater than 200
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=50, width=250))
        # THEN
        self.assertEqual(rule, self.PackageBoxSetupRule)

    def test_07_match_setup_rule_by_all_layout_constraints(self):
        # GIVEN
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': 'sheet',
                    'min_layout_width': 100,
                    'max_layout_width': 150,
                    'min_layout_length': 200,
                    'max_layout_length': 250,
                },
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': 'sheet',
                    'min_layout_width': 50,
                    'max_layout_width': 100,
                    'min_layout_length': 150,
                    'max_layout_length': 200,
                },
            ],
        )
        setup_1_rule_1, setup_2_rule_1 = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 1, 'setup_qty': 0},
            ]
        )
        # WHEN layout matches second setup
        rule = (setup_1 | setup_2).match_setup_rule(100, Layout2D(length=160, width=50))
        # THEN
        self.assertEqual(rule, setup_2_rule_1)
        # WHEN layout matches first setup
        rule = (setup_1 | setup_2).match_setup_rule(
            100, Layout2D(length=230, width=110)
        )
        # THEN
        self.assertEqual(rule, setup_1_rule_1)

    def test_08_not_match_setup_rule_by_layout_constraints(self):
        # GIVEN
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': 'sheet',
                    'min_layout_width': 100,
                    'max_layout_width': 150,
                    'min_layout_length': 200,
                    'max_layout_length': 250,
                },
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': 'sheet',
                    'min_layout_width': 50,
                    'max_layout_width': 100,
                    'min_layout_length': 150,
                    'max_layout_length': 200,
                },
            ],
        )
        setup_1_rule_1, setup_2_rule_1 = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 1, 'setup_qty': 0},
            ]
        )
        # WHEN layout matches second setup
        rule = (setup_1 | setup_2).match_setup_rule(
            100, Layout2D(length=5000, width=5000)
        )
        # THEN
        self.assertEqual(rule, self.PackageBoxSetupRule)

    def test_09_match_setup_rule_by_box_type_single(self):
        # GIVEN
        box_type_1, box_type_2 = self.PackageBoxType.create(
            [{'name': 'BT1'}, {'name': 'BT1'}]
        )
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': 'sheet',
                    'box_type_ids': [(4, box_type_1.id)],
                },
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': 'sheet',
                    'box_type_ids': [(4, box_type_2.id)],
                },
            ],
        )
        setup_1_rule_1, setup_2_rule_1 = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 1, 'setup_qty': 0},
            ]
        )
        # WHEN
        rule = (setup_1 | setup_2).match_setup_rule(100, box_type=box_type_2)
        # THEN
        self.assertEqual(rule, setup_2_rule_1)

    def test_10_match_setup_rule_by_box_type_multi(self):
        # GIVEN
        box_type_1, box_type_2 = self.PackageBoxType.create(
            [{'name': 'BT1'}, {'name': 'BT1'}]
        )
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': 'sheet',
                    'box_type_ids': [(4, box_type_1.id), (4, box_type_2.id)],
                },
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': 'sheet',
                    'box_type_ids': [(4, box_type_2.id)],
                },
            ],
        )
        setup_1_rule_1, setup_2_rule_1 = self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1, 'setup_qty': 0},
                {'setup_id': setup_2.id, 'min_qty': 1, 'setup_qty': 0},
            ]
        )
        # WHEN
        rule = (setup_1 | setup_2).match_setup_rule(100, box_type=box_type_2)
        # THEN
        self.assertEqual(rule, setup_1_rule_1)

from .. import const
from . import common


class TestPackageConfiguratorBoxSetup(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})
        cls.print_house_1 = cls.PackagePrintHouse.create(
            {
                'name': 'MY-PRINTING-HOUSE-1',
            }
        )
        cls.color_1 = cls.PackagePrintColor.create({'name': 'MY-COLOR-1'})

    def test_01_configure_box_do_setup_sheet_type_all(self):
        # GIVEN
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': 'sheet',
                    'sequence': 20,
                },
                # To try matching this first!
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': 'sheet',
                    'sequence': 10,
                },
            ],
        )
        setup_1_rule_1, setup_2_rule_1 = self.PackageBoxSetupRule.create(
            [
                # To be used for first circulation
                {'setup_id': setup_1.id, 'min_qty': 50, 'setup_qty': 100},
                # To be used for second circulation
                {'setup_id': setup_2.id, 'min_qty': 150, 'setup_qty': 200},
            ]
        )
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        (
            comp_base_greyboard,
            comp_lid_greyboard,
            comp_base_wrappingpaper_inside,
            comp_base_wrappingpaper_outside,
            comp_lid_wrappingpaper_inside,
            comp_lid_wrappingpaper_outside,
        ) = self.PackageConfiguratorBoxComponent.create(
            [
                {
                    'component_type': 'base_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type': 'lid_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type': 'base_wrappingpaper_inside',
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type': 'base_wrappingpaper_outside',
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type': 'lid_wrappingpaper_inside',
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type': 'lid_wrappingpaper_outside',
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
            ]
        )
        circulation_1, circulation_2 = self.PackageConfiguratorBoxCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
        )
        # WHEN
        cfg.action_setup()
        # THEN
        # Quantities
        # grey board layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(comp_base_greyboard.fit_qty, 27)
        self.assertEqual(comp_base_wrappingpaper_inside.fit_qty, 9)
        self.assertEqual(comp_base_wrappingpaper_outside.fit_qty, 6)
        self.assertEqual(comp_lid_greyboard.fit_qty, 27)
        self.assertEqual(comp_lid_wrappingpaper_inside.fit_qty, 9)
        self.assertEqual(comp_lid_wrappingpaper_outside.fit_qty, 5)
        # Circulations
        # With 100 box circulation
        # Setup
        # For each part.
        circ_items = circulation_1.item_ids
        self.assertEqual(len(circ_items), 6)
        # One setup per component.
        self.assertEqual(len(circ_items.mapped('circulation_setup_ids')), 6)
        item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(item_base_greyboard.circulation_setup_ids.setup_raw_qty, 4)
        self.assertEqual(item_base_greyboard.quantity, 8)
        item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(item_lid_greyboard.circulation_setup_ids.setup_raw_qty, 4)
        self.assertEqual(item_lid_greyboard.quantity, 8)

        item_base_wrappingpaper_inside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_inside'
        )
        self.assertEqual(
            item_base_wrappingpaper_inside.circulation_setup_ids.setup_raw_qty, 12
        )
        self.assertEqual(item_base_wrappingpaper_inside.quantity, 24)

        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type == 'lid_wrappingpaper_inside'
            ).circulation_setup_ids.setup_raw_qty,
            12,
        )
        item_base_wrappingpaper_outside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_outside'
        )
        self.assertEqual(
            item_base_wrappingpaper_outside.circulation_setup_ids.setup_raw_qty, 17
        )
        self.assertEqual(item_base_wrappingpaper_outside.quantity, 34)
        item_lid_wrappingpaper_outside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_wrappingpaper_outside'
        )
        self.assertEqual(
            item_lid_wrappingpaper_outside.circulation_setup_ids.setup_raw_qty, 20
        )
        self.assertEqual(item_lid_wrappingpaper_outside.quantity, 40)
        self.assertEqual(circulation_1.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_1.total_lamination_outside_cost, 0.0)
        # With setup
        # (8+4+4)*0.05 + (24+12+12)*0.04 + (37+17+20)*0.06
        self.assertEqual(circulation_1.total_cost, 7.159999999999999)
        # 7.159999999999999 / 100
        self.assertEqual(circulation_1.unit_cost, 0.0716)
        # With 200 box circulation
        circ_items = circulation_2.item_ids
        self.assertEqual(len(circ_items), 6)
        self.assertEqual(len(circ_items.mapped('circulation_setup_ids')), 6)
        # setup_qty is 200 and fit qty is 27, so 200/27
        item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(item_base_greyboard.circulation_setup_ids.setup_raw_qty, 8)
        self.assertEqual(item_base_greyboard.quantity, 16)
        # 200/9
        item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(item_lid_greyboard.circulation_setup_ids.setup_raw_qty, 8)
        self.assertEqual(item_lid_greyboard.quantity, 16)
        # 200/6
        item_base_wrappingpaper_inside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_inside'
        )
        self.assertEqual(
            item_base_wrappingpaper_inside.circulation_setup_ids.setup_raw_qty, 23
        )
        self.assertEqual(item_base_wrappingpaper_inside.quantity, 46)
        # 200/27
        item_lid_wrappingpaper_inside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_wrappingpaper_inside'
        )
        self.assertEqual(
            item_lid_wrappingpaper_inside.circulation_setup_ids.setup_raw_qty, 23
        )
        self.assertEqual(item_lid_wrappingpaper_inside.quantity, 46)
        # 200/9
        item_base_wrappingpaper_outside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_outside'
        )
        self.assertEqual(
            item_base_wrappingpaper_outside.circulation_setup_ids.setup_raw_qty, 34
        )
        self.assertEqual(item_base_wrappingpaper_outside.quantity, 68)
        # 200/5
        item_lid_wrappingpaper_outside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_wrappingpaper_outside'
        )
        self.assertEqual(
            item_lid_wrappingpaper_outside.circulation_setup_ids.setup_raw_qty, 40
        )
        self.assertEqual(item_lid_wrappingpaper_outside.quantity, 80)
        self.assertEqual(circulation_2.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_2.total_lamination_outside_cost, 0.0)
        # With setup
        # (16+8+8)*0.05 + (46+23+23)*0.04 + (74+34+40)*0.06
        self.assertEqual(circulation_2.total_cost, 14.16)
        # 14.16 / 200
        self.assertEqual(circulation_2.unit_cost, 0.0708)

    def test_02_configure_box_do_setup_sheet_type_some(self):
        # GIVEN
        setup_1, setup_2, setup_print = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': const.SetupType.SHEET,
                    'sequence': 20,
                },
                # To try matching this first!
                {
                    'name': 'MY-BOX-SHEET-SETUP-2',
                    'setup_type': const.SetupType.SHEET,
                    'sequence': 10,
                },
                {
                    'name': 'MY-BOX-PRINT-SETUP-1',
                    'setup_type': const.SetupType.PRINT,
                    'sequence': 5,
                },
            ],
        )
        self.PackageBoxSetupRule.create(
            [
                # To be used for first circulation
                {'setup_id': setup_1.id, 'min_qty': 50, 'setup_qty': 100},
                # To be used for second circulation
                {'setup_id': setup_2.id, 'min_qty': 150, 'setup_qty': 200},
                # This is expected to be ignored, because printing house is not selected
                {'setup_id': setup_print.id, 'min_qty': 1, 'setup_qty': 1000},
            ]
        )
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        (
            comp_base_greyboard,
            comp_lid_greyboard,
        ) = self.PackageConfiguratorBoxComponent.create(
            [
                {
                    'component_type': 'base_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type': 'lid_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
            ]
        )
        circulation_1, circulation_2 = self.PackageConfiguratorBoxCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
        )
        # WHEN
        cfg.action_setup()
        # THEN
        # Quantities
        # grey board layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(comp_base_greyboard.fit_qty, 27)
        self.assertEqual(comp_lid_greyboard.fit_qty, 27)
        # Circulations
        # With 100 box circulation
        circ_items = circulation_1.item_ids
        self.assertEqual(len(circ_items), 2)
        # One setup per component.
        self.assertEqual(len(circ_items.mapped('circulation_setup_ids')), 2)
        item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(item_base_greyboard.circulation_setup_ids.setup_raw_qty, 4)
        self.assertEqual(item_base_greyboard.quantity, 8)
        item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(item_lid_greyboard.circulation_setup_ids.setup_raw_qty, 4)
        self.assertEqual(item_lid_greyboard.quantity, 8)
        self.assertEqual(circulation_1.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_1.total_lamination_outside_cost, 0.0)
        # With setup
        # (8+4+4)*0.05
        self.assertEqual(circulation_1.total_cost, 0.7999999999999999)
        # 0.8 / 100
        self.assertEqual(circulation_1.unit_cost, 0.008)
        # With 200 box circulation
        circ_items = circulation_2.item_ids
        self.assertEqual(len(circ_items), 2)
        # One setup per component.
        self.assertEqual(len(circ_items.mapped('circulation_setup_ids')), 2)
        item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(item_base_greyboard.circulation_setup_ids.setup_raw_qty, 8)
        self.assertEqual(item_base_greyboard.quantity, 16)
        item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(item_lid_greyboard.circulation_setup_ids.setup_raw_qty, 8)
        self.assertEqual(item_lid_greyboard.quantity, 16)
        self.assertEqual(circulation_2.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_2.total_lamination_outside_cost, 0.0)
        # (16+8+8)*0.05
        self.assertEqual(circulation_2.total_cost, 1.5999999999999999)
        # 1.6 / 200
        self.assertEqual(circulation_2.unit_cost, 0.008)

    def test_03_configure_box_do_setup_print_type_some(self):
        # GIVEN
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-PRINT-SETUP-1',
                    'setup_type': const.SetupType.PRINT,
                    'sequence': 20,
                },
                # To try matching this first!
                {
                    'name': 'MY-BOX-PRINT-SETUP-2',
                    'setup_type': const.SetupType.PRINT,
                    'sequence': 10,
                },
            ],
        )
        self.PackageBoxSetupRule.create(
            [
                # To be used for first circulation
                {'setup_id': setup_1.id, 'min_qty': 50, 'setup_qty': 100},
                # To be used for second circulation
                {'setup_id': setup_2.id, 'min_qty': 150, 'setup_qty': 200},
            ]
        )
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'print_house_id': self.print_house_1.id,
            }
        )
        (
            comp_base_greyboard,
            comp_lid_greyboard,
        ) = self.PackageConfiguratorBoxComponent.create(
            [
                {
                    'component_type': 'base_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                    'print_color_id': self.color_1.id,
                },
                {
                    'component_type': 'lid_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                    'print_color_id': self.color_1.id,
                },
            ]
        )
        circulation_1, circulation_2 = self.PackageConfiguratorBoxCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
        )
        # WHEN
        cfg.action_setup()
        # THEN
        # Quantities
        # grey board layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(comp_base_greyboard.fit_qty, 27)
        self.assertEqual(comp_lid_greyboard.fit_qty, 27)
        # Circulations
        # With 100 box circulation
        circ_items = circulation_1.item_ids
        self.assertEqual(len(circ_items), 2)
        # One setup per component.
        self.assertEqual(len(circ_items.mapped('circulation_setup_ids')), 2)
        item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(item_base_greyboard.circulation_setup_ids.setup_raw_qty, 4)
        self.assertEqual(item_base_greyboard.quantity, 8)
        item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(item_lid_greyboard.circulation_setup_ids.setup_raw_qty, 4)
        self.assertEqual(item_lid_greyboard.quantity, 8)
        self.assertEqual(circulation_1.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_1.total_lamination_outside_cost, 0.0)
        # With setup
        # (8+4+4)*0.05
        self.assertEqual(circulation_1.total_cost, 0.7999999999999999)
        # 0.8 / 100
        self.assertEqual(circulation_1.unit_cost, 0.008)
        # With 200 box circulation
        circ_items = circulation_2.item_ids
        self.assertEqual(len(circ_items), 2)
        # One setup per component.
        self.assertEqual(len(circ_items.mapped('circulation_setup_ids')), 2)
        item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(item_base_greyboard.circulation_setup_ids.setup_raw_qty, 8)
        self.assertEqual(item_base_greyboard.quantity, 16)
        item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(item_lid_greyboard.circulation_setup_ids.setup_raw_qty, 8)
        self.assertEqual(item_lid_greyboard.quantity, 16)
        self.assertEqual(circulation_2.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_2.total_lamination_outside_cost, 0.0)
        # (16+8+8)*0.05
        self.assertEqual(circulation_2.total_cost, 1.5999999999999999)
        # 1.6 / 200
        self.assertEqual(circulation_2.unit_cost, 0.008)

    def test_04_configure_box_do_setup_sheet_n_print_type(self):
        # GIVEN
        setup_1, setup_2 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-SHEET-SETUP-1',
                    'setup_type': const.SetupType.SHEET,
                    'sequence': 10,
                },
                {
                    'name': 'MY-BOX-PRINT-SETUP-2',
                    'setup_type': const.SetupType.PRINT,
                    'sequence': 20,
                },
            ],
        )
        self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1, 'setup_qty': 100},
                {'setup_id': setup_2.id, 'min_qty': 1, 'setup_qty': 100},
            ]
        )
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'print_house_id': self.print_house_1.id,
            }
        )
        self.PackageConfiguratorBoxComponent.create(
            [
                {
                    'component_type': 'base_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                    'print_color_id': self.color_1.id,
                },
                {
                    'component_type': 'lid_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                    'print_color_id': self.color_1.id,
                },
            ]
        )
        circulation_1, circulation_2 = self.PackageConfiguratorBoxCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
        )
        # WHEN
        cfg.action_setup()
        # THEN
        # Quantities
        # Circulations
        # With 100 box circulation
        circ_items = circulation_1.item_ids
        self.assertEqual(len(circ_items), 2)
        # Two setups per component (for each setup type).
        self.assertEqual(len(circ_items.mapped('circulation_setup_ids')), 4)
        setup_base_greyboards = circ_items.mapped('circulation_setup_ids').filtered(
            lambda r: r.circulation_item_id.component_id.component_type
            == 'base_greyboard'
        )
        self.assertEqual(len(setup_base_greyboards), 2)
        setup_lid_greyboards = circ_items.mapped('circulation_setup_ids').filtered(
            lambda r: r.circulation_item_id.component_id.component_type
            == 'lid_greyboard'
        )
        self.assertEqual(len(setup_lid_greyboards), 2)
        # With setup
        # With 200 box circulation
        circ_items = circulation_2.item_ids
        self.assertEqual(len(circ_items), 2)
        # Two setups per component (for each setup type).
        self.assertEqual(len(circ_items.mapped('circulation_setup_ids')), 4)
        setup_base_greyboards = circ_items.mapped('circulation_setup_ids').filtered(
            lambda r: r.circulation_item_id.component_id.component_type
            == 'base_greyboard'
        )
        self.assertEqual(len(setup_base_greyboards), 2)
        setup_lid_greyboards = circ_items.mapped('circulation_setup_ids').filtered(
            lambda r: r.circulation_item_id.component_id.component_type
            == 'lid_greyboard'
        )
        self.assertEqual(len(setup_lid_greyboards), 2)

    def test_05_configure_box_do_setup_print_no_color(self):
        # GIVEN
        setup_1 = self.PackageBoxSetup.create(
            [
                {
                    'name': 'MY-BOX-PRINT-SETUP-2',
                    'setup_type': const.SetupType.PRINT,
                    'sequence': 20,
                },
            ],
        )
        self.PackageBoxSetupRule.create(
            [
                {'setup_id': setup_1.id, 'min_qty': 1, 'setup_qty': 100},
            ]
        )
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'print_house_id': self.print_house_1.id,
            }
        )
        self.PackageConfiguratorBoxComponent.create(
            [
                {
                    'component_type': 'base_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type': 'lid_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
            ]
        )
        circulation_1, circulation_2 = self.PackageConfiguratorBoxCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
        )
        # WHEN
        cfg.action_setup()
        # THEN
        # Quantities
        # Circulations
        # With 100 box circulation
        circ_items = circulation_1.item_ids
        self.assertEqual(len(circ_items), 2)
        # No color set on any of components, so setup is ignored.
        self.assertEqual(len(circ_items.mapped('circulation_setup_ids')), 0)
        # With setup
        # With 200 box circulation
        circ_items = circulation_2.item_ids
        self.assertEqual(len(circ_items), 2)
        self.assertEqual(len(circ_items.mapped('circulation_setup_ids')), 0)

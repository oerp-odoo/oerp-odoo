from . import common


class TestPackageConfiguratorBoxSetup(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})

    def test_01_configure_box_do_setup_all_sheet_parts(self):
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
                # thickness: 1.5mm
                'carton_base_id': self.package_carton_1.id,
                'carton_lid_id': self.package_carton_1.id,
                'wrappingpaper_base_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_base_outside_id': self.package_wrappingpaper_2.id,
                'wrappingpaper_lid_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_lid_outside_id': self.package_wrappingpaper_2.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
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
        # Layouts
        self.assertEqual(cfg.base_layout_length, 224)
        self.assertEqual(cfg.base_layout_width, 101)
        self.assertEqual(cfg.base_inside_wrapping_length, 224)
        self.assertEqual(cfg.base_inside_wrapping_width, 101)
        self.assertEqual(cfg.base_outside_wrapping_length, 264)
        self.assertEqual(cfg.base_outside_wrapping_width, 141)
        self.assertEqual(cfg.lid_layout_length, 232)
        self.assertEqual(cfg.lid_layout_width, 109)
        self.assertEqual(cfg.lid_inside_wrapping_length, 232)
        self.assertEqual(cfg.lid_inside_wrapping_width, 109)
        self.assertEqual(cfg.lid_outside_wrapping_length, 272)
        self.assertEqual(cfg.lid_outside_wrapping_width, 149)
        # Quantities
        # carton layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(cfg.base_layout_fit_qty, 27)
        self.assertEqual(cfg.base_inside_fit_qty, 9)
        self.assertEqual(cfg.base_outside_fit_qty, 6)
        self.assertEqual(cfg.lid_layout_fit_qty, 27)
        self.assertEqual(cfg.lid_inside_fit_qty, 9)
        self.assertEqual(cfg.lid_outside_fit_qty, 5)
        # Circulations
        # With 100 box circulation
        # Setup
        # For each part.
        self.assertEqual(len(circulation_1.circulation_setup_ids), 6)
        self.assertEqual(
            circulation_1.circulation_setup_ids.mapped('setup_rule_id'), setup_1_rule_1
        )
        self.assertEqual(
            set(circulation_1.circulation_setup_ids.mapped('part')),
            {
                'base_carton',
                'lid_carton',
                'base_inside_wrapping',
                'base_outside_wrapping',
                'lid_inside_wrapping',
                'lid_outside_wrapping',
            },
        )
        # setup_qty is 100 and fit qty is 27, so 100/27
        self.assertEqual(
            circulation_1.circulation_setup_ids.filtered(
                lambda r: r.part == 'base_carton'
            ).setup_raw_qty,
            4,
        )
        # 100/9
        self.assertEqual(
            circulation_1.circulation_setup_ids.filtered(
                lambda r: r.part == 'base_inside_wrapping'
            ).setup_raw_qty,
            12,
        )
        # 100/6
        self.assertEqual(
            circulation_1.circulation_setup_ids.filtered(
                lambda r: r.part == 'base_outside_wrapping'
            ).setup_raw_qty,
            17,
        )
        # 100/27
        self.assertEqual(
            circulation_1.circulation_setup_ids.filtered(
                lambda r: r.part == 'lid_carton'
            ).setup_raw_qty,
            4,
        )
        # 100/9
        self.assertEqual(
            circulation_1.circulation_setup_ids.filtered(
                lambda r: r.part == 'lid_inside_wrapping'
            ).setup_raw_qty,
            12,
        )
        # 100/5
        self.assertEqual(
            circulation_1.circulation_setup_ids.filtered(
                lambda r: r.part == 'lid_outside_wrapping'
            ).setup_raw_qty,
            20,
        )
        # 4+4 from base with setup and 4+4 from lid, with setup
        self.assertEqual(circulation_1.total_base_carton_quantity, 8)
        self.assertEqual(circulation_1.total_lid_carton_quantity, 8)
        # 12+12 from base with setup, 12+12 from lid with setup
        self.assertEqual(circulation_1.total_base_inside_wrappingpaper_quantity, 24)
        self.assertEqual(circulation_1.total_lid_inside_wrappingpaper_quantity, 24)
        # 17+17 from base with setup, 20+20 from lid with setup.
        self.assertEqual(circulation_1.total_base_outside_wrappingpaper_quantity, 34)
        self.assertEqual(circulation_1.total_lid_outside_wrappingpaper_quantity, 40)
        self.assertEqual(circulation_1.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_1.total_lamination_outside_cost, 0.0)
        # With setup
        # (8+4+4)*0.05 + (24+12+12)*0.04 + (37+17+20)*0.06
        self.assertEqual(circulation_1.total_cost, 7.159999999999999)
        # 7.159999999999999 / 100
        self.assertEqual(circulation_1.unit_cost, 0.0716)
        # With 200 box circulation
        self.assertEqual(len(circulation_2.circulation_setup_ids), 6)
        self.assertEqual(
            circulation_2.circulation_setup_ids.mapped('setup_rule_id'), setup_2_rule_1
        )
        self.assertEqual(
            set(circulation_2.circulation_setup_ids.mapped('part')),
            {
                'base_carton',
                'lid_carton',
                'base_inside_wrapping',
                'base_outside_wrapping',
                'lid_inside_wrapping',
                'lid_outside_wrapping',
            },
        )
        # setup_qty is 200 and fit qty is 27, so 200/27
        self.assertEqual(
            circulation_2.circulation_setup_ids.filtered(
                lambda r: r.part == 'base_carton'
            ).setup_raw_qty,
            8,
        )
        # 200/9
        self.assertEqual(
            circulation_2.circulation_setup_ids.filtered(
                lambda r: r.part == 'base_inside_wrapping'
            ).setup_raw_qty,
            23,
        )
        # 200/6
        self.assertEqual(
            circulation_2.circulation_setup_ids.filtered(
                lambda r: r.part == 'base_outside_wrapping'
            ).setup_raw_qty,
            34,
        )
        # 200/27
        self.assertEqual(
            circulation_2.circulation_setup_ids.filtered(
                lambda r: r.part == 'lid_carton'
            ).setup_raw_qty,
            8,
        )
        # 200/9
        self.assertEqual(
            circulation_2.circulation_setup_ids.filtered(
                lambda r: r.part == 'lid_inside_wrapping'
            ).setup_raw_qty,
            23,
        )
        # 200/5
        self.assertEqual(
            circulation_2.circulation_setup_ids.filtered(
                lambda r: r.part == 'lid_outside_wrapping'
            ).setup_raw_qty,
            40,
        )
        # 8+8 from base with setup and 8+8 from lid with setup
        self.assertEqual(circulation_2.total_base_carton_quantity, 16)
        self.assertEqual(circulation_2.total_lid_carton_quantity, 16)
        # 23+23 from base with setup, 23+23 from lid with setup
        self.assertEqual(circulation_2.total_base_inside_wrappingpaper_quantity, 46)
        self.assertEqual(circulation_2.total_lid_inside_wrappingpaper_quantity, 46)
        # 34+34 from base with setup, 40+40 from lid with setup.
        self.assertEqual(circulation_2.total_base_outside_wrappingpaper_quantity, 68)
        self.assertEqual(circulation_2.total_lid_outside_wrappingpaper_quantity, 80)
        self.assertEqual(circulation_2.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_2.total_lamination_outside_cost, 0.0)
        # With setup
        # (16+8+8)*0.05 + (46+23+23)*0.04 + (74+34+40)*0.06
        self.assertEqual(circulation_2.total_cost, 14.16)
        # 14.16 / 200
        self.assertEqual(circulation_2.unit_cost, 0.0708)

    def test_02_configure_box_do_setup_only_carton(self):
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
                # thickness: 1.5mm
                'carton_base_id': self.package_carton_1.id,
                'carton_lid_id': self.package_carton_1.id,
                'wrappingpaper_base_inside_id': False,
                'wrappingpaper_base_outside_id': False,
                'wrappingpaper_lid_inside_id': False,
                'wrappingpaper_lid_outside_id': False,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
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
        # Layouts
        self.assertEqual(cfg.base_layout_length, 224)
        self.assertEqual(cfg.base_layout_width, 101)
        self.assertEqual(cfg.base_inside_wrapping_length, 224)
        self.assertEqual(cfg.base_inside_wrapping_width, 101)
        self.assertEqual(cfg.base_outside_wrapping_length, 264)
        self.assertEqual(cfg.base_outside_wrapping_width, 141)
        self.assertEqual(cfg.lid_layout_length, 232)
        self.assertEqual(cfg.lid_layout_width, 109)
        self.assertEqual(cfg.lid_inside_wrapping_length, 232)
        self.assertEqual(cfg.lid_inside_wrapping_width, 109)
        self.assertEqual(cfg.lid_outside_wrapping_length, 272)
        self.assertEqual(cfg.lid_outside_wrapping_width, 149)
        # Quantities
        # carton layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(cfg.base_layout_fit_qty, 27)
        self.assertEqual(cfg.base_inside_fit_qty, 0)
        self.assertEqual(cfg.base_outside_fit_qty, 0)
        self.assertEqual(cfg.lid_layout_fit_qty, 27)
        self.assertEqual(cfg.lid_inside_fit_qty, 0)
        self.assertEqual(cfg.lid_outside_fit_qty, 0)
        # Circulations
        # With 100 box circulation
        # For 1 for base carton + 1 for lid carton.
        self.assertEqual(len(circulation_1.circulation_setup_ids), 2)
        self.assertEqual(
            circulation_1.circulation_setup_ids.mapped('setup_rule_id'), setup_1_rule_1
        )
        self.assertEqual(
            set(circulation_1.circulation_setup_ids.mapped('part')),
            {'base_carton', 'lid_carton'},
        )
        # 100/27
        self.assertEqual(
            circulation_1.circulation_setup_ids.filtered(
                lambda r: r.part == 'base_carton'
            ).setup_raw_qty,
            4,
        )
        # 100/27
        self.assertEqual(
            circulation_1.circulation_setup_ids.filtered(
                lambda r: r.part == 'lid_carton'
            ).setup_raw_qty,
            4,
        )
        # 4+4 from base with setup and 4+4 from lid with setup
        self.assertEqual(circulation_1.total_base_carton_quantity, 8)
        self.assertEqual(circulation_1.total_lid_carton_quantity, 8)
        # 12 from base, 12 from lid
        self.assertEqual(circulation_1.total_base_inside_wrappingpaper_quantity, 0)
        self.assertEqual(circulation_1.total_lid_inside_wrappingpaper_quantity, 0)
        # 17 from base, 20 from lid.
        self.assertEqual(circulation_1.total_base_outside_wrappingpaper_quantity, 0)
        self.assertEqual(circulation_1.total_lid_outside_wrappingpaper_quantity, 0)
        self.assertEqual(circulation_1.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_1.total_lamination_outside_cost, 0.0)
        # With setup
        # (8+4+4)*0.05
        self.assertEqual(circulation_1.total_cost, 0.7999999999999999)
        # 0.8 / 100
        self.assertEqual(circulation_1.unit_cost, 0.008)
        # With 200 box circulation
        self.assertEqual(len(circulation_2.circulation_setup_ids), 2)
        self.assertEqual(
            circulation_2.circulation_setup_ids.mapped('setup_rule_id'), setup_2_rule_1
        )
        self.assertEqual(
            set(circulation_2.circulation_setup_ids.mapped('part')),
            {'base_carton', 'lid_carton'},
        )
        # 200/27
        self.assertEqual(
            circulation_2.circulation_setup_ids.filtered(
                lambda r: r.part == 'base_carton'
            ).setup_raw_qty,
            8,
        )
        # 200/27
        self.assertEqual(
            circulation_2.circulation_setup_ids.filtered(
                lambda r: r.part == 'lid_carton'
            ).setup_raw_qty,
            8,
        )
        # 8+8 from base with setup and 8+8 from lid with setup
        self.assertEqual(circulation_2.total_base_carton_quantity, 16)
        self.assertEqual(circulation_2.total_lid_carton_quantity, 16)
        self.assertEqual(circulation_2.total_base_inside_wrappingpaper_quantity, 0)
        self.assertEqual(circulation_2.total_lid_inside_wrappingpaper_quantity, 0)
        self.assertEqual(circulation_2.total_base_outside_wrappingpaper_quantity, 0)
        self.assertEqual(circulation_2.total_lid_outside_wrappingpaper_quantity, 0)
        self.assertEqual(circulation_2.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_2.total_lamination_outside_cost, 0.0)
        # (16+8+8)*0.05
        self.assertEqual(circulation_2.total_cost, 1.5999999999999999)
        # 1.6 / 200
        self.assertEqual(circulation_2.unit_cost, 0.008)

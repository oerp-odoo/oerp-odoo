from . import common


class TestPackageConfiguratorBox(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_kind_box_1 = cls.PackageKind.create(
            {'name': 'MY-BOX-TYPE-1', 'package_type_id': cls.package_type_box.id}
        )

    def test_01_configure_box_basic(self):
        # WHEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': self.package_type_box.id,
            },
        )
        (
            comp_base,
            comp_lid,
            comp_base_wrappingpaper_inside,
            comp_base_wrappingpaper_outside,
            comp_lid_wrappingpaper_inside,
            comp_lid_wrappingpaper_outside,
        ) = self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': self.component_type_lid.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_lid_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_lid_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
            ]
        )
        # THEN
        # Layouts
        self.assertEqual(comp_base.component_length, 224)
        self.assertEqual(comp_base.component_width, 101)
        self.assertEqual(comp_base_wrappingpaper_inside.component_length, 224)
        self.assertEqual(comp_base_wrappingpaper_inside.component_width, 101)
        self.assertEqual(comp_base_wrappingpaper_outside.component_length, 264)
        self.assertEqual(comp_base_wrappingpaper_outside.component_width, 141)
        self.assertEqual(comp_lid.component_length, 232)
        self.assertEqual(comp_lid.component_width, 109)
        self.assertEqual(comp_lid_wrappingpaper_inside.component_length, 232)
        self.assertEqual(comp_lid_wrappingpaper_inside.component_width, 109)
        self.assertEqual(comp_lid_wrappingpaper_outside.component_length, 272)
        self.assertEqual(comp_lid_wrappingpaper_outside.component_width, 149)
        # Quantities
        # grey board layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        # Fit Quantity
        self.assertEqual(comp_base.fit_qty, 27)
        self.assertEqual(comp_base_wrappingpaper_inside.fit_qty, 9)
        self.assertEqual(comp_base_wrappingpaper_outside.fit_qty, 6)
        self.assertEqual(comp_lid.fit_qty, 27)
        self.assertEqual(comp_lid_wrappingpaper_inside.fit_qty, 9)
        self.assertEqual(comp_lid_wrappingpaper_outside.fit_qty, 5)

    def test_02_configure_box_with_circulation(self):
        # GIVEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': self.package_type_box.id,
            }
        )
        (
            comp_base,
            comp_lid,
            comp_base_wrappingpaper_inside,
            comp_base_wrappingpaper_outside,
            comp_lid_wrappingpaper_inside,
            comp_lid_wrappingpaper_outside,
        ) = self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': self.component_type_lid.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_lid_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_lid_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
            ]
        )
        # WHEN
        circulation_1, circulation_2 = self.PackageConfiguratorCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
        )
        # THEN
        # Layouts
        self.assertEqual(comp_base.component_length, 224)
        self.assertEqual(comp_base.component_width, 101)
        self.assertEqual(comp_base_wrappingpaper_inside.component_length, 224)
        self.assertEqual(comp_base_wrappingpaper_inside.component_width, 101)
        self.assertEqual(comp_base_wrappingpaper_outside.component_length, 264)
        self.assertEqual(comp_base_wrappingpaper_outside.component_width, 141)
        self.assertEqual(comp_lid.component_length, 232)
        self.assertEqual(comp_lid.component_width, 109)
        self.assertEqual(comp_lid_wrappingpaper_inside.component_length, 232)
        self.assertEqual(comp_lid_wrappingpaper_inside.component_width, 109)
        self.assertEqual(comp_lid_wrappingpaper_outside.component_length, 272)
        self.assertEqual(comp_lid_wrappingpaper_outside.component_width, 149)
        # Quantities
        # grey board layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(comp_base.fit_qty, 27)
        self.assertEqual(comp_base_wrappingpaper_inside.fit_qty, 9)
        self.assertEqual(comp_base_wrappingpaper_outside.fit_qty, 6)
        self.assertEqual(comp_lid.fit_qty, 27)
        self.assertEqual(comp_lid_wrappingpaper_inside.fit_qty, 9)
        self.assertEqual(comp_lid_wrappingpaper_outside.fit_qty, 5)
        # Circulations
        # Circulation Components
        circ_items = circulation_1.item_ids
        self.assertEqual(len(circ_items), 6)
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code == 'base'
            ).quantity,
            4,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code == 'lid'
            ).quantity,
            4,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'base_wrappingpaper_inside'
            ).quantity,
            12,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'lid_wrappingpaper_inside'
            ).quantity,
            12,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'base_wrappingpaper_outside'
            ).quantity,
            17,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'lid_wrappingpaper_outside'
            ).quantity,
            20,
        )
        # With 100 box circulation
        # 8*0.05 + 24*0.04 + 37*0.06
        self.assertEqual(circulation_1.total_cost, 3.5799999999999996)
        # 3.5799999999999996 / 100
        self.assertEqual(circulation_1.unit_cost, 0.0358)
        # With 200 box circulation
        circ_items = circulation_2.item_ids
        self.assertEqual(len(circ_items), 6)
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code == 'base'
            ).quantity,
            8,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code == 'lid'
            ).quantity,
            8,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'base_wrappingpaper_inside'
            ).quantity,
            23,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'lid_wrappingpaper_inside'
            ).quantity,
            23,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'base_wrappingpaper_outside'
            ).quantity,
            34,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'lid_wrappingpaper_outside'
            ).quantity,
            40,
        )
        # 16*0.05 + 46*0.04 + 74*0.06
        self.assertEqual(circulation_2.total_cost, 7.08)
        # 7.08 / 200
        self.assertEqual(circulation_2.unit_cost, 0.0354)

    def test_03_configure_box_with_circulation_n_min_qty(self):
        # GIVEN
        self.package_sheet_greyboard_1.min_qty = 10
        # Inside
        self.package_sheet_wrappingpaper_1.min_qty = 24
        # Outside
        self.package_sheet_wrappingpaper_2.min_qty = 50
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': self.package_type_box.id,
            }
        )
        (
            comp_base,
            comp_lid,
            comp_base_wrappingpaper_inside,
            comp_base_wrappingpaper_outside,
            comp_lid_wrappingpaper_inside,
            comp_lid_wrappingpaper_outside,
        ) = self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': self.component_type_lid.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_lid_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_lid_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
            ]
        )
        # WHEN
        circulation_1, circulation_2 = self.PackageConfiguratorCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
        )
        # THEN
        # Layouts
        # Quantities
        # grey board layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(comp_base.fit_qty, 27)
        self.assertEqual(comp_base_wrappingpaper_inside.fit_qty, 9)
        self.assertEqual(comp_base_wrappingpaper_outside.fit_qty, 6)
        self.assertEqual(comp_lid.fit_qty, 27)
        self.assertEqual(comp_lid_wrappingpaper_inside.fit_qty, 9)
        self.assertEqual(comp_lid_wrappingpaper_outside.fit_qty, 5)
        # Circulations
        # With 100 box circulation
        circ_items = circulation_1.item_ids
        self.assertEqual(len(circ_items), 6)
        # 4 from base and 4 from lid, but min_qty = 10
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code == 'base'
            ).quantity,
            5,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code == 'lid'
            ).quantity,
            5,
        )
        # 12 from base, 12 from lid and min_qty = 24
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'base_wrappingpaper_inside'
            ).quantity,
            12,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'lid_wrappingpaper_inside'
            ).quantity,
            12,
        )
        # 17 from base, 20 from lid. and min_qty = 50, so we increase it proportionally
        # 37/50 = 0.74 and then 17/0.74 = 23 (rounded up) and 20/0.74 = 27 (
        # rounded down)
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'base_wrappingpaper_outside'
            ).quantity,
            23,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'lid_wrappingpaper_outside'
            ).quantity,
            27,
        )
        # 10*0.05 + 24*0.04 + 50*0.06
        self.assertEqual(circulation_1.total_cost, 4.46)
        # 4.46 / 100
        self.assertEqual(circulation_1.unit_cost, 0.0446)
        # With 200 box circulation
        circ_items = circulation_2.item_ids
        self.assertEqual(len(circ_items), 6)
        # 8 from base and 8 from lid
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code == 'base'
            ).quantity,
            8,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code == 'lid'
            ).quantity,
            8,
        )
        # 23 from base, 23 from lid
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'base_wrappingpaper_inside'
            ).quantity,
            23,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'lid_wrappingpaper_inside'
            ).quantity,
            23,
        )
        # 34 from base, 40 from lid.
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'base_wrappingpaper_outside'
            ).quantity,
            34,
        )
        self.assertEqual(
            circ_items.filtered(
                lambda r: r.component_id.component_type_id.code
                == 'lid_wrappingpaper_outside'
            ).quantity,
            40,
        )
        # 16*0.05 + 46*0.04 + 74*0.06
        self.assertEqual(circulation_2.total_cost, 7.08)
        # 7.08 / 200
        self.assertEqual(circulation_2.unit_cost, 0.0354)

    def test_04_configure_box_missing_base_height(self):
        # GIVEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 0.0,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': self.package_type_box.id,
            }
        )
        # WHEN
        (
            comp_base,
            comp_lid,
            comp_base_wrappingpaper_inside,
            comp_base_wrappingpaper_outside,
            comp_lid_wrappingpaper_inside,
            comp_lid_wrappingpaper_outside,
        ) = self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': self.component_type_lid.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_lid_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_lid_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
            ]
        )
        # THEN
        self.assertEqual(comp_base.component_length, 0)
        self.assertEqual(comp_base.component_width, 0)
        self.assertEqual(comp_base_wrappingpaper_inside.component_length, 0)
        self.assertEqual(comp_base_wrappingpaper_inside.component_width, 0)
        self.assertEqual(comp_base_wrappingpaper_outside.component_length, 0)
        self.assertEqual(comp_base_wrappingpaper_outside.component_width, 0)
        self.assertEqual(comp_lid.component_length, 0)
        self.assertEqual(comp_lid.component_width, 0)
        self.assertEqual(comp_lid_wrappingpaper_inside.component_length, 0)
        self.assertEqual(comp_lid_wrappingpaper_inside.component_width, 0)
        self.assertEqual(comp_lid_wrappingpaper_outside.component_length, 0)
        self.assertEqual(comp_lid_wrappingpaper_outside.component_width, 0)

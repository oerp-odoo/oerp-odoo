from . import common


class TestPackageConfiguratorBoxPrintCost(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})
        cls.color_1, cls.color_2 = cls.PackagePrintColor.create(
            [
                {'name': 'MY-COLOR-1'},
                {'name': 'MY-COLOR-2'},
            ]
        )
        cls.print_pricelist_1 = cls.PackagePrintPricelist.create(
            {'name': 'MY-PRICELIST-1'}
        )
        cls.print_house_1 = cls.PackagePrintHouse.create(
            {
                'name': 'MY-PRINTING-HOUSE-1',
                'print_pricelist_id': cls.print_pricelist_1.id,
            }
        )

    def test_01_configure_box_print_cost_same_sheet_different_colors(self):
        self.PackagePrintPricelistRule.create(
            [
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_1.id,
                    'min_qty': 1,
                    'unit_cost': 10,
                },
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_1.id,
                    'min_qty': 30,
                    'unit_cost': 5,
                },
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_2.id,
                    'min_qty': 1,
                    'unit_cost': 12,
                },
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_2.id,
                    'min_qty': 30,
                    'unit_cost': 6,
                },
            ]
        )
        # GIVEN
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
            comp_base_wrappingpaper_inside,
            comp_base_wrappingpaper_outside,
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
                    'print_color_id': self.color_1.id,
                },
                {
                    'component_type': 'base_wrappingpaper_outside',
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                    'print_color_id': self.color_2.id,
                },
            ]
        )
        # WHEN
        circulation_1, circulation_2 = self.PackageConfiguratorBoxCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
        )
        # THEN
        # Quantities
        # grey board layout is 1000x700 (mm)
        # outside wrappingpaper layout is 700x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(comp_base_greyboard.fit_qty, 27)
        self.assertEqual(comp_base_wrappingpaper_inside.fit_qty, 9)
        self.assertEqual(comp_base_wrappingpaper_outside.fit_qty, 4)
        self.assertEqual(comp_lid_greyboard.fit_qty, 27)
        # Circulations
        # With 100 box circulation
        # Circulation Components
        circ_items = circulation_1.item_ids
        self.assertEqual(len(circ_items), 4)
        circ_item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(circ_item_base_greyboard.quantity, 4)
        self.assertEqual(circ_item_base_greyboard.print_unit_cost, 0.0)
        circ_item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(circ_item_lid_greyboard.quantity, 4)
        self.assertEqual(circ_item_lid_greyboard.print_unit_cost, 0.0)

        circ_item_base_wrappingpaper_inside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_inside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_inside.quantity, 12)
        self.assertEqual(circ_item_base_wrappingpaper_inside.print_unit_cost, 10)
        circ_item_base_wrappingpaper_outside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_outside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_outside.quantity, 25)
        # Rule to have lower price must have minimum 30 quantity.
        self.assertEqual(circ_item_base_wrappingpaper_outside.print_unit_cost, 12)
        # 8*0.05 + 12*0.04 + 25*0.04 (using same sheet for base wrapping inside/outside)
        # + (print cost) 12*10+25*12
        self.assertEqual(circulation_1.total_cost, 421.88)
        # 421.88 / 100
        self.assertEqual(circulation_1.unit_cost, 4.2188)
        # With 200 box circulation
        circ_items = circulation_2.item_ids
        self.assertEqual(len(circ_items), 4)

        circ_item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(circ_item_base_greyboard.quantity, 8)
        self.assertEqual(circ_item_base_greyboard.print_unit_cost, 0.0)
        circ_item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(circ_item_lid_greyboard.quantity, 8)
        self.assertEqual(circ_item_lid_greyboard.print_unit_cost, 0.0)

        circ_item_base_wrappingpaper_inside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_inside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_inside.quantity, 23)
        self.assertEqual(circ_item_base_wrappingpaper_inside.print_unit_cost, 10)
        circ_item_base_wrappingpaper_outside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_outside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_outside.quantity, 50)
        self.assertEqual(circ_item_base_wrappingpaper_outside.print_unit_cost, 6)
        # 16*0.05 + 23*0.04 + 50*0.04
        # + (print cost) 23*10+50*6
        self.assertEqual(circulation_2.total_cost, 533.7199999999999998)
        # 533.7199999999999998 / 200
        self.assertEqual(circulation_2.unit_cost, 2.6686)

    def test_02_configure_box_print_cost_same_color_different_sheets(self):
        # GIVEN
        self.PackagePrintPricelistRule.create(
            [
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_1.id,
                    'min_qty': 1,
                    'unit_cost': 10,
                },
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_1.id,
                    'min_qty': 20,
                    'unit_cost': 5,
                },
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_2.id,
                    'min_qty': 1,
                    'unit_cost': 12,
                },
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_2.id,
                    'min_qty': 20,
                    'unit_cost': 6,
                },
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
            comp_base_wrappingpaper_inside,
            comp_base_wrappingpaper_outside,
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
                    'print_color_id': self.color_1.id,
                },
                {
                    'component_type': 'base_wrappingpaper_outside',
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                    'print_color_id': self.color_1.id,
                },
            ]
        )
        # WHEN
        circulation_1, circulation_2 = self.PackageConfiguratorBoxCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
        )
        # THEN
        # Quantities
        # grey board layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(comp_base_greyboard.fit_qty, 27)
        self.assertEqual(comp_base_wrappingpaper_inside.fit_qty, 9)
        self.assertEqual(comp_base_wrappingpaper_outside.fit_qty, 6)
        self.assertEqual(comp_lid_greyboard.fit_qty, 27)
        # Circulations
        # With 100 box circulation
        # Circulation Components
        circ_items = circulation_1.item_ids
        self.assertEqual(len(circ_items), 4)
        circ_item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(circ_item_base_greyboard.quantity, 4)
        self.assertEqual(circ_item_base_greyboard.print_unit_cost, 0.0)
        circ_item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(circ_item_lid_greyboard.quantity, 4)
        self.assertEqual(circ_item_lid_greyboard.print_unit_cost, 0.0)

        circ_item_base_wrappingpaper_inside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_inside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_inside.quantity, 12)
        self.assertEqual(circ_item_base_wrappingpaper_inside.print_unit_cost, 10)
        circ_item_base_wrappingpaper_outside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_outside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_outside.quantity, 17)
        # Rule to have lower price must have minimum 20 quantity.
        self.assertEqual(circ_item_base_wrappingpaper_outside.print_unit_cost, 10)
        # 8*0.05 + 12*0.04 + 17*0.06
        # + (print cost) 12*10+17*10
        self.assertEqual(circulation_1.total_cost, 291.9)
        # 291.9 / 100
        self.assertEqual(circulation_1.unit_cost, 2.919)
        # With 200 box circulation
        circ_items = circulation_2.item_ids
        self.assertEqual(len(circ_items), 4)

        circ_item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(circ_item_base_greyboard.quantity, 8)
        self.assertEqual(circ_item_base_greyboard.print_unit_cost, 0.0)
        circ_item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(circ_item_lid_greyboard.quantity, 8)
        self.assertEqual(circ_item_lid_greyboard.print_unit_cost, 0.0)

        circ_item_base_wrappingpaper_inside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_inside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_inside.quantity, 23)
        self.assertEqual(circ_item_base_wrappingpaper_inside.print_unit_cost, 5)
        circ_item_base_wrappingpaper_outside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_outside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_outside.quantity, 34)
        self.assertEqual(circ_item_base_wrappingpaper_outside.print_unit_cost, 5)
        # 16*0.05 + 23*0.04 + 34*0.06
        # + (print cost) 23*5+34*5
        self.assertEqual(circulation_2.total_cost, 288.76)
        # 288.76 / 200
        self.assertEqual(circulation_2.unit_cost, 1.4438)

    def test_03_configure_box_print_cost_same_color_n_sheet(self):
        # GIVEN
        self.PackagePrintPricelistRule.create(
            [
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_1.id,
                    'min_qty': 1,
                    'unit_cost': 10,
                },
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_1.id,
                    'min_qty': 30,
                    'unit_cost': 5,
                },
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_2.id,
                    'min_qty': 1,
                    'unit_cost': 12,
                },
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_2.id,
                    'min_qty': 30,
                    'unit_cost': 6,
                },
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
            comp_base_wrappingpaper_inside,
            comp_base_wrappingpaper_outside,
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
                    'print_color_id': self.color_1.id,
                },
                {
                    'component_type': 'base_wrappingpaper_outside',
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                    'print_color_id': self.color_1.id,
                },
            ]
        )
        # WHEN
        circulation_1, circulation_2 = self.PackageConfiguratorBoxCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
        )
        # THEN
        # Quantities
        # grey board layout is 1000x700 (mm)
        # outside wrappingpaper layout is 700x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(comp_base_greyboard.fit_qty, 27)
        self.assertEqual(comp_base_wrappingpaper_inside.fit_qty, 9)
        self.assertEqual(comp_base_wrappingpaper_outside.fit_qty, 4)
        self.assertEqual(comp_lid_greyboard.fit_qty, 27)
        # Circulations
        # With 100 box circulation
        # Circulation Components
        circ_items = circulation_1.item_ids
        self.assertEqual(len(circ_items), 4)
        circ_item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(circ_item_base_greyboard.quantity, 4)
        self.assertEqual(circ_item_base_greyboard.print_unit_cost, 0.0)
        circ_item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(circ_item_lid_greyboard.quantity, 4)
        self.assertEqual(circ_item_lid_greyboard.print_unit_cost, 0.0)

        circ_item_base_wrappingpaper_inside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_inside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_inside.quantity, 12)
        # When we have same color and material used for printing, quantity is grouped,
        # so even if single component needs 12 raw sheets, we need (12+25)=37 raw sheets
        # in totals over two components. That means, it matches rule with lower cost!
        self.assertEqual(circ_item_base_wrappingpaper_inside.print_unit_cost, 5)
        circ_item_base_wrappingpaper_outside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_outside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_outside.quantity, 25)
        self.assertEqual(circ_item_base_wrappingpaper_outside.print_unit_cost, 5)
        # 8*0.05 + 12*0.04 + 25*0.04 (using same sheet for base wrapping inside/outside)
        # + (print cost) 12*5+25*5
        self.assertEqual(circulation_1.total_cost, 186.88)
        # 186.88 / 100
        self.assertEqual(circulation_1.unit_cost, 1.8688)
        # With 200 box circulation
        circ_items = circulation_2.item_ids
        self.assertEqual(len(circ_items), 4)

        circ_item_base_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_greyboard'
        )
        self.assertEqual(circ_item_base_greyboard.quantity, 8)
        self.assertEqual(circ_item_base_greyboard.print_unit_cost, 0.0)
        circ_item_lid_greyboard = circ_items.filtered(
            lambda r: r.component_id.component_type == 'lid_greyboard'
        )
        self.assertEqual(circ_item_lid_greyboard.quantity, 8)
        self.assertEqual(circ_item_lid_greyboard.print_unit_cost, 0.0)

        circ_item_base_wrappingpaper_inside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_inside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_inside.quantity, 23)
        self.assertEqual(circ_item_base_wrappingpaper_inside.print_unit_cost, 5)
        circ_item_base_wrappingpaper_outside = circ_items.filtered(
            lambda r: r.component_id.component_type == 'base_wrappingpaper_outside'
        )
        self.assertEqual(circ_item_base_wrappingpaper_outside.quantity, 50)
        self.assertEqual(circ_item_base_wrappingpaper_outside.print_unit_cost, 5)
        # 16*0.05 + 23*0.04 + 50*0.04
        # + (print cost) 23*5+50*5
        self.assertEqual(circulation_2.total_cost, 368.71999999999997)
        # 368.71999999999997 / 200
        self.assertEqual(circulation_2.unit_cost, 1.8436)

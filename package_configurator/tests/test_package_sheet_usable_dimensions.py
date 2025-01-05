from . import common


class TestPackageSheetUsableDimensions(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_kind_box_1 = cls.PackageKind.create(
            {'name': 'MY-BOX-TYPE-1', 'package_type_id': cls.package_type_box.id}
        )
        cls.print_house_1 = cls.PackagePrintHouse.create({'name': 'MY-PRINT-HOUSE-1'})
        cls.print_color_1 = cls.PackagePrintColor.create({'name': 'Color 1'})

    def test_01_sheet_usable_dimensions_no_print_house(self):
        # GIVEN
        self.package_sheet_greyboard_1.write({'sheet_length': 1000, 'sheet_width': 700})
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
        comp_base = self.PackageConfiguratorComponent.create(
            {
                'component_type_id': self.component_type_base.id,
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': cfg.id,
                'print_color_id': self.print_color_1.id,
            },
        )
        # THEN
        self.assertEqual(comp_base.sheet_usable_length, 1000)
        self.assertEqual(comp_base.sheet_usable_width, 700)

    def test_02_sheet_usable_dimensions_print_house_lower_dimensions(self):
        # GIVEN
        self.package_sheet_greyboard_1.write({'sheet_length': 1000, 'sheet_width': 700})
        self.print_house_1.write({'print_max_length': 900, 'print_max_width': 600})
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
                'print_house_id': self.print_house_1.id,
                'package_type_id': self.package_type_box.id,
            },
        )
        comp_base = self.PackageConfiguratorComponent.create(
            {
                'component_type_id': self.component_type_base.id,
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': cfg.id,
                'print_color_id': self.print_color_1.id,
            },
        )
        # THEN
        self.assertEqual(comp_base.sheet_usable_length, 900)
        self.assertEqual(comp_base.sheet_usable_width, 600)

    def test_03_sheet_usable_dimensions_print_house_lower_dimensions_no_color(self):
        # GIVEN
        self.package_sheet_greyboard_1.write({'sheet_length': 1000, 'sheet_width': 700})
        self.print_house_1.write({'print_max_length': 900, 'print_max_width': 600})
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
                'print_house_id': self.print_house_1.id,
                'package_type_id': self.package_type_box.id,
            },
        )
        comp_base = self.PackageConfiguratorComponent.create(
            {
                'component_type_id': self.component_type_base.id,
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': cfg.id,
                'print_color_id': False,
            },
        )
        # THEN
        self.assertEqual(comp_base.sheet_usable_length, 1000)
        self.assertEqual(comp_base.sheet_usable_width, 700)

    def test_04_sheet_usable_dimensions_print_house_higher_dimensions(self):
        # GIVEN
        self.package_sheet_greyboard_1.write({'sheet_length': 1000, 'sheet_width': 700})
        self.print_house_1.write({'print_max_length': 1200, 'print_max_width': 800})
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
                'print_house_id': self.print_house_1.id,
                'package_type_id': self.package_type_box.id,
            },
        )
        comp_base = self.PackageConfiguratorComponent.create(
            {
                'component_type_id': self.component_type_base.id,
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': cfg.id,
                'print_color_id': self.print_color_1.id,
            },
        )
        # THEN
        self.assertEqual(comp_base.sheet_usable_length, 1000)
        self.assertEqual(comp_base.sheet_usable_width, 700)

    def test_05_sheet_usable_dimensions_print_house_higher_no_limit(self):
        # GIVEN
        self.package_sheet_greyboard_1.write({'sheet_length': 1000, 'sheet_width': 700})
        self.print_house_1.write({'print_max_length': 0, 'print_max_width': 0})
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
                'print_house_id': self.print_house_1.id,
                'package_type_id': self.package_type_box.id,
            },
        )
        comp_base = self.PackageConfiguratorComponent.create(
            {
                'component_type_id': self.component_type_base.id,
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': cfg.id,
                'print_color_id': self.print_color_1.id,
            },
        )
        # THEN
        self.assertEqual(comp_base.sheet_usable_length, 1000)
        self.assertEqual(comp_base.sheet_usable_width, 700)

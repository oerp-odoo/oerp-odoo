from . import common


class TestPackageSheetUsableDimensions(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})
        cls.print_house_1 = cls.PackagePrintHouse.create({'name': 'MY-PRINT-HOUSE-1'})

    def test_01_sheet_usable_dimensions_no_print_house(self):
        # GIVEN
        self.package_sheet_greyboard_1.write({'sheet_length': 1000, 'sheet_width': 700})
        # WHEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            },
        )
        comp_base_greyboard = self.PackageConfiguratorBoxComponent.create(
            {
                'component_type': 'base_greyboard',
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': cfg.id,
            },
        )
        # THEN
        self.assertEqual(comp_base_greyboard.sheet_usable_length, 1000)
        self.assertEqual(comp_base_greyboard.sheet_usable_width, 700)

    def test_02_sheet_usable_dimensions_print_house_lower_dimensions(self):
        # GIVEN
        self.package_sheet_greyboard_1.write({'sheet_length': 1000, 'sheet_width': 700})
        self.print_house_1.write({'print_max_length': 900, 'print_max_width': 600})
        # WHEN
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
            },
        )
        comp_base_greyboard = self.PackageConfiguratorBoxComponent.create(
            {
                'component_type': 'base_greyboard',
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': cfg.id,
            },
        )
        # THEN
        self.assertEqual(comp_base_greyboard.sheet_usable_length, 900)
        self.assertEqual(comp_base_greyboard.sheet_usable_width, 600)

    def test_03_sheet_usable_dimensions_print_house_higher_dimensions(self):
        # GIVEN
        self.package_sheet_greyboard_1.write({'sheet_length': 1000, 'sheet_width': 700})
        self.print_house_1.write({'print_max_length': 1200, 'print_max_width': 800})
        # WHEN
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
            },
        )
        comp_base_greyboard = self.PackageConfiguratorBoxComponent.create(
            {
                'component_type': 'base_greyboard',
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': cfg.id,
            },
        )
        # THEN
        self.assertEqual(comp_base_greyboard.sheet_usable_length, 1000)
        self.assertEqual(comp_base_greyboard.sheet_usable_width, 700)

    def test_04_sheet_usable_dimensions_print_house_higher_no_limit(self):
        # GIVEN
        self.package_sheet_greyboard_1.write({'sheet_length': 1000, 'sheet_width': 700})
        self.print_house_1.write({'print_max_length': 0, 'print_max_width': 0})
        # WHEN
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
            },
        )
        comp_base_greyboard = self.PackageConfiguratorBoxComponent.create(
            {
                'component_type': 'base_greyboard',
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': cfg.id,
            },
        )
        # THEN
        self.assertEqual(comp_base_greyboard.sheet_usable_length, 1000)
        self.assertEqual(comp_base_greyboard.sheet_usable_width, 700)

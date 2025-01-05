from . import common


class TestDefaultByContextCode(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})
        (
            cls.package_sheet_type_greyboard_1,
            cls.package_sheet_type_wrappingpaper_1,
        ) = cls.PackageSheetType.create(
            [
                {
                    'name': 'Orange/orange',
                    'thickness': 1.5,
                    'thickness_uom': 'mm',
                    'component_kind_id': cls.component_kind_greyboard.id,
                },
                {
                    'name': 'Some Art 1',
                    'thickness': 150,
                    'thickness_uom': 'gsm',
                    'component_kind_id': cls.component_kind_wrappingpaper.id,
                },
            ]
        )

    def test_01_default_package_type_box(self):
        # WHEN
        cfg = self.PackageConfigurator.with_context(package_type_code='box').create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
            }
        )
        # THEN
        self.assertEqual(cfg.package_type_id, self.package_type_box)

    def test_02_default_package_type_insert(self):
        # WHEN
        cfg = self.PackageConfigurator.with_context(package_type_code='insert').create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
            }
        )
        # THEN
        self.assertEqual(cfg.package_type_id, self.package_type_insert)

    def test_03_package_sheet_default_component_kind_greyboard(self):
        # WHEN
        sheet = self.PackageSheet.with_context(
            package_component_kind_code='greyboard'
        ).create(
            {
                'sheet_type_id': self.package_sheet_type_greyboard_1.id,
                'sheet_length': 1000,
                'sheet_width': 700,
                'unit_cost': 0.05,
            }
        )
        # THEN
        self.assertEqual(sheet.component_kind_id, self.component_kind_greyboard)

    def test_04_package_sheet_default_component_kind_wrappingpaper(self):
        # WHEN
        sheet = self.PackageSheet.with_context(
            package_component_kind_code='wrappingpaper'
        ).create(
            {
                'sheet_type_id': self.package_sheet_type_wrappingpaper_1.id,
                'sheet_length': 1000,
                'sheet_width': 700,
                'unit_cost': 0.05,
            }
        )
        # THEN
        self.assertEqual(sheet.component_kind_id, self.component_kind_wrappingpaper)

    def test_05_package_sheet_type_default_component_kind_greyboard(self):
        # WHEN
        sheet_type = self.PackageSheetType.with_context(
            package_component_kind_code='greyboard'
        ).create(
            {
                'name': 'Blue/blue',
                'thickness': 1.5,
                'thickness_uom': 'mm',
            }
        )
        # THEN
        self.assertEqual(sheet_type.component_kind_id, self.component_kind_greyboard)

    def test_06_package_sheet_type_default_component_kind_wrappingpaper(self):
        # WHEN
        sheet_type = self.PackageSheetType.with_context(
            package_component_kind_code='wrappingpaper'
        ).create(
            {
                'name': 'Art Paper',
                'thickness': 150,
                'thickness_uom': 'gsm',
            }
        )
        # THEN
        self.assertEqual(
            sheet_type.component_kind_id, self.component_kind_wrappingpaper
        )

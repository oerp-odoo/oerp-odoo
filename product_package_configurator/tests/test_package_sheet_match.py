from odoo.addons.base.tests.common import BaseCommon

from ..value_objects.layout import Layout2D


class TestPackageSheetMatch(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PackageSheetType = cls.env['package.sheet.type']
        cls.PackageSheetGreyboard = cls.env['package.sheet.greyboard']
        cls.PackageSheetWrappingpaper = cls.env['package.sheet.wrappingpaper']
        cls.PackageSheetMatch = cls.env['package.sheet.match']
        (
            cls.package_sheet_type_greyboard_1,
            cls.package_sheet_type_wrappingpaper_1,
        ) = cls.PackageSheetType.create(
            [
                {
                    'name': 'Orange/orange',
                    'thickness': 1.5,
                    'thickness_uom': 'mm',
                    'scope': 'greyboard',
                },
                {
                    'name': 'Some Art 1',
                    'thickness': 150,
                    'thickness_uom': 'gsm',
                    'scope': 'wrappingpaper',
                },
            ]
        )

    def test_01_package_sheet_match_greyboard_best_fit(self):
        # GIVEN
        _gb_1, _gb_2, gb_3 = self.PackageSheetGreyboard.create(
            [
                {
                    'sheet_type_id': self.package_sheet_type_greyboard_1.id,
                    'sheet_width': 500,
                    'sheet_length': 1000,
                    'unit_cost': 2,
                },
                {
                    'sheet_type_id': self.package_sheet_type_greyboard_1.id,
                    'sheet_width': 600,
                    'sheet_length': 1000,
                    'unit_cost': 2,
                },
                {
                    'sheet_type_id': self.package_sheet_type_greyboard_1.id,
                    'sheet_width': 700,
                    'sheet_length': 1000,
                    'unit_cost': 2,
                },
            ]
        )
        # WHEN
        res = self.PackageSheetMatch.match(
            self.package_sheet_type_greyboard_1, Layout2D(length=10, width=10)
        )
        # THEN
        self.assertEqual(res, gb_3)

    def test_02_package_sheet_match_greyboard_best_unit_price(self):
        # GIVEN
        gb_1, _gb_2, _gb_3 = self.PackageSheetGreyboard.create(
            [
                {
                    'sheet_type_id': self.package_sheet_type_greyboard_1.id,
                    'sheet_width': 500,
                    'sheet_length': 1000,
                    'unit_cost': 2,
                },
                {
                    'sheet_type_id': self.package_sheet_type_greyboard_1.id,
                    'sheet_width': 600,
                    'sheet_length': 1000,
                    'unit_cost': 200,
                },
                {
                    'sheet_type_id': self.package_sheet_type_greyboard_1.id,
                    'sheet_width': 700,
                    'sheet_length': 1000,
                    'unit_cost': 300,
                },
            ]
        )
        # WHEN
        res = self.PackageSheetMatch.match(
            self.package_sheet_type_greyboard_1, Layout2D(length=10, width=10)
        )
        # THEN
        self.assertEqual(res, gb_1)

    def test_03_package_sheet_match_greyboard_no_fit(self):
        # WHEN
        res = self.PackageSheetMatch.match(
            self.package_sheet_type_greyboard_1, Layout2D(length=10, width=10)
        )
        # THEN
        self.assertEqual(res, self.PackageSheetGreyboard)

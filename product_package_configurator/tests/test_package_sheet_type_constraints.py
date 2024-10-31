from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon

from .. import const


class TestPackageSheetConstraints(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PackageSheetType = cls.env['package.sheet.type']
        cls.PackageSheet = cls.env['package.sheet']
        cls.PackageSheetMatch = cls.env['package.sheet.match']
        (cls.package_sheet_type_greyboard_1,) = cls.PackageSheetType.create(
            [
                {
                    'name': 'Orange/orange',
                    'thickness': 1.5,
                    'thickness_uom': 'mm',
                    'scope': const.SheetTypeScope.GREYBOARD,
                },
            ]
        )

    def test_01_package_sheet_type_greyboard_use_gsm_uom(self):
        with self.assertRaisesRegex(
            ValidationError, r"Grey Board must use mm UoM for Thickness!"
        ):
            self.PackageSheetType.create(
                [
                    {
                        'name': 'Orange/orange',
                        'thickness': 1.5,
                        'thickness_uom': 'gsm',
                        'scope': const.SheetTypeScope.GREYBOARD,
                    },
                ]
            )

    def test_02_package_sheet_type_greyboard_use_gsm_uom(self):
        with self.assertRaisesRegex(
            ValidationError, r"Wrapping Paper must use gsm UoM for Thickness!"
        ):
            self.PackageSheetType.create(
                [
                    {
                        'name': 'ABC',
                        'thickness': 1.5,
                        'thickness_uom': 'mm',
                        'scope': const.SheetTypeScope.WRAPPINGPAPER,
                    },
                ]
            )

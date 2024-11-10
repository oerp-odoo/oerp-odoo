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

    def test_01_package_sheet_scope_mismatch(self):
        with self.assertRaisesRegex(
            ValidationError, r"Sheet \(.+\) and its Type \(.+\) must match same Scope!"
        ):
            self.PackageSheet.create(
                {
                    'sheet_type_id': self.package_sheet_type_greyboard_1.id,
                    'sheet_width': 500,
                    'sheet_length': 1000,
                    'unit_cost': 2,
                    'scope': const.SheetTypeScope.WRAPPINGPAPER,
                }
            )

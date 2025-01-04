from odoo.exceptions import ValidationError
from odoo.fields import Command

from .common import TestProductPackageConfiguratorCommon


class TestPackageSheetConstraints(TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        (cls.package_sheet_type_greyboard_1,) = cls.PackageSheetType.create(
            [
                {
                    'name': 'Orange/orange',
                    'thickness': 1.5,
                    'thickness_uom': 'mm',
                    'component_kind_ids': [
                        Command.set([cls.component_kind_greyboard.id])
                    ],
                },
            ]
        )

    def test_01_package_sheet_kind_mismatch(self):
        with self.assertRaisesRegex(
            ValidationError, r"Sheet \(.+\) and its Type \(.+\) must match at least"
        ):
            self.PackageSheet.create(
                {
                    'sheet_type_id': self.package_sheet_type_greyboard_1.id,
                    'sheet_width': 500,
                    'sheet_length': 1000,
                    'unit_cost': 2,
                    'component_kind_ids': [
                        Command.set([self.component_kind_wrappingpaper.id])
                    ],
                }
            )

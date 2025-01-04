from odoo.exceptions import ValidationError
from odoo.fields import Command

from .common import TestProductPackageConfiguratorCommon


class TestPackageSheetTypeConstraints(TestProductPackageConfiguratorCommon):
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

    def test_01_package_sheet_type_greyboard_use_gsm_uom(self):
        with self.assertRaisesRegex(
            ValidationError, r"Orange/orange must use mm UoM for Thickness!"
        ):
            self.PackageSheetType.create(
                [
                    {
                        'name': 'Orange/orange',
                        'thickness': 1.5,
                        'thickness_uom': 'gsm',
                        'component_kind_ids': [
                            Command.set([self.component_kind_greyboard.id])
                        ],
                    },
                ]
            )

    def test_02_package_sheet_type_greyboard_use_gsm_uom(self):
        with self.assertRaisesRegex(
            ValidationError, r"ABC must use gsm UoM for Thickness!"
        ):
            self.PackageSheetType.create(
                [
                    {
                        'name': 'ABC',
                        'thickness': 1.5,
                        'thickness_uom': 'mm',
                        'component_kind_ids': [
                            Command.set([self.component_kind_wrappingpaper.id])
                        ],
                    },
                ]
            )

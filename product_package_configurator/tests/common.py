from odoo.tests.common import TransactionCase


class TestProductPackageConfiguratorCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.PackageConfiguratorBox = cls.env['package.configurator.box']
        cls.PackageConfiguratorBoxCirculation = cls.env[
            'package.configurator.box.circulation'
        ]
        cls.PackageBoxSetup = cls.env['package.box.setup']
        cls.PackageBoxSetupRule = cls.env['package.box.setup.rule']
        cls.PackageBoxType = cls.env['package.box.type']
        cls.PackageSheetType = cls.env['package.sheet.type']
        cls.PackageSheetGreyboard = cls.env['package.sheet.greyboard']
        cls.PackageWrappingpaper = cls.env['package.wrappingpaper']
        cls.PackageBoxLayout = cls.env['package.box.layout']
        cls.PackageLamination = cls.env['package.lamination']
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
        cls.package_sheet_greyboard_1 = cls.PackageSheetGreyboard.create(
            {
                'sheet_type_id': cls.package_sheet_type_greyboard_1.id,
                'sheet_length': 1000,
                'sheet_width': 700,
                'unit_cost': 0.05,
            }
        )
        cls.package_wrappingpaper_1 = cls.PackageWrappingpaper.create(
            {
                'sheet_type_id': cls.package_sheet_type_wrappingpaper_1.id,
                'sheet_length': 700,
                'sheet_width': 400,
                'unit_cost': 0.04,
            }
        )
        cls.package_wrappingpaper_2 = cls.PackageWrappingpaper.create(
            {
                'sheet_type_id': cls.package_sheet_type_wrappingpaper_1.id,
                'sheet_length': 800,
                'sheet_width': 400,
                'unit_cost': 0.06,
            }
        )
        cls.package_lamination_1 = cls.PackageLamination.create(
            {
                'name': 'Lamination 1',
                'unit_cost': 2,
            }
        )

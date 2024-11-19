from odoo.tests.common import TransactionCase

from .. import const


class TestProductPackageConfiguratorCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.PackagePrintHouse = cls.env['package.print.house']
        cls.PackageDefaultComponent = cls.env['package.default.component']
        cls.PackageConfiguratorBox = cls.env['package.configurator.box']
        cls.PackageConfiguratorBoxComponent = cls.env[
            'package.configurator.box.component'
        ]
        cls.PackageConfiguratorBoxCirculation = cls.env[
            'package.configurator.box.circulation'
        ]
        cls.PackagePrintColor = cls.env['package.print.color']
        cls.PackageBoxSetup = cls.env['package.box.setup']
        cls.PackageBoxSetupRule = cls.env['package.box.setup.rule']
        cls.PackagePrintHouse = cls.env['package.print.house']
        cls.PackagePrintPricelist = cls.env['package.print.pricelist']
        cls.PackagePrintPricelistRule = cls.env['package.print.pricelist.rule']
        cls.PackageBoxType = cls.env['package.box.type']
        cls.PackageSheetType = cls.env['package.sheet.type']
        cls.PackageSheet = cls.env['package.sheet']
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
                    'scope': const.SheetTypeScope.GREYBOARD,
                },
                {
                    'name': 'Some Art 1',
                    'thickness': 150,
                    'thickness_uom': 'gsm',
                    'scope': const.SheetTypeScope.WRAPPINGPAPER,
                },
            ]
        )
        cls.package_sheet_greyboard_1 = cls.PackageSheet.create(
            {
                'sheet_type_id': cls.package_sheet_type_greyboard_1.id,
                'sheet_length': 1000,
                'sheet_width': 700,
                'unit_cost': 0.05,
                'scope': const.SheetTypeScope.GREYBOARD,
            }
        )
        cls.package_sheet_wrappingpaper_1 = cls.PackageSheet.create(
            {
                'sheet_type_id': cls.package_sheet_type_wrappingpaper_1.id,
                'sheet_length': 700,
                'sheet_width': 400,
                'unit_cost': 0.04,
                'scope': const.SheetTypeScope.WRAPPINGPAPER,
            }
        )
        cls.package_sheet_wrappingpaper_2 = cls.PackageSheet.create(
            {
                'sheet_type_id': cls.package_sheet_type_wrappingpaper_1.id,
                'sheet_length': 800,
                'sheet_width': 400,
                'unit_cost': 0.06,
                'scope': const.SheetTypeScope.WRAPPINGPAPER,
            }
        )
        cls.package_lamination_1 = cls.PackageLamination.create(
            {
                'name': 'Lamination 1',
                'unit_cost': 2,
            }
        )

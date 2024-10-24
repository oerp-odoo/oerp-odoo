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
        cls.PackageCarton = cls.env['package.carton']
        cls.PackageWrappingpaper = cls.env['package.wrappingpaper']
        cls.PackageBoxLayout = cls.env['package.box.layout']
        cls.PackageLamination = cls.env['package.lamination']
        cls.package_carton_1 = cls.PackageCarton.create(
            {
                'name': 'Carton 1.5mm',
                'thickness': 1.5,
                'sheet_length': 1000,
                'sheet_width': 700,
                'unit_cost': 0.05,
            }
        )
        cls.package_wrappingpaper_1 = cls.PackageWrappingpaper.create(
            {
                'name': 'Wrapping 1',
                'sheet_length': 700,
                'sheet_width': 400,
                'unit_cost': 0.04,
            }
        )
        cls.package_wrappingpaper_2 = cls.PackageWrappingpaper.create(
            {
                'name': 'Wrapping 2',
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

from odoo.tests.common import TransactionCase


class TestProductPackageConfiguratorCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.PackageConfiguratorBox = cls.env['package.configurator.box']
        cls.PackageBoxType = cls.env['package.box.type']
        cls.PackageCarton = cls.env['package.carton']
        cls.PackageBoxLayout = cls.env['package.box.layout']
        cls.PackageLamination = cls.env['package.lamination']
        cls.package_carton_1 = cls.PackageCarton.create(
            {
                'name': 'Carton 1.5mm',
                'thickness': 1.5,
            }
        )
        cls.package_lamination_1 = cls.PackageLamination.create(
            {
                'name': 'Lamination 1',
                'price_unit': 2,
            }
        )

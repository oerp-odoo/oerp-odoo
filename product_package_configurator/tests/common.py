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
        cls.package_carton_1 = cls.PackageCarton.create(
            {
                'name': 'Carton 1.5mm',
                'thickness': 1.5,
            }
        )

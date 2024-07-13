from odoo.tests.common import TransactionCase


class TestProductPackageConfiguratorCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.PackageConfiguratorBox = cls.env['package.configurator.box']
        cls.PackageBoxType = cls.env['package.box.type']
        cls.PackageBoxLayout = cls.env['package.box.layout']

from odoo.tests.common import TransactionCase


class TestCategoryHsCode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.product_category_all = cls.env.ref('product.product_category_all')

    def test_01_create_product_with_category_hs_code(self):
        # GIVEN
        self.product_category_all.hs_code = '123456'
        # WHEN
        product = self.ProductProduct.create(
            {'name': 'P1', 'categ_id': self.product_category_all.id}
        )
        # THEN
        self.assertEqual(product.hs_code, '123456')

    def test_02_create_product_with_default_category_hs_code(self):
        # GIVEN
        self.product_category_all.hs_code = '123456'
        # WHEN
        product = self.ProductProduct.create({'name': 'P1'})
        # THEN
        self.assertEqual(product.hs_code, '123456')

    def test_03_create_product_forcing_custom_hs_code(self):
        # GIVEN
        self.product_category_all.hs_code = '123456'
        # WHEN
        product = self.ProductProduct.create(
            {
                'name': 'P1',
                'categ_id': self.product_category_all.id,
                'hs_code': '11223344',
            }
        )
        # THEN
        self.assertEqual(product.hs_code, '11223344')

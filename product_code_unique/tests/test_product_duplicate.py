from . import common


class TestProductDuplicate(common.TestProductCommon):
    """Tests to check duplication of products."""

    def test_01_product_duplicate(self):
        """Test case with `product.template`."""
        product_tmpl = self.product_1.product_tmpl_id.copy()
        self.assertEqual(
            product_tmpl.default_code,
            'E-COM07 (copy)',
            "Product Template was not correctly duplicated!",
        )

    def test_02_product_duplicate(self):
        """Test case with `product.product`."""
        product = self.product_1.copy()
        self.assertEqual(
            product.default_code,
            'E-COM07 (copy)',
            "Product was not correctly duplicated!",
        )

    def test_03_product_duplicate(self):
        """Duplicate default_code when default is truthy string."""
        product = self.product_1.copy(default={'default_code': 'TEST_CODE'})
        self.assertEqual(
            product.default_code,
            'TEST_CODE',
            "Product was not correctly duplicated!",
        )

    def test_04_product_duplicate(self):
        """Duplicate default_code when default is False."""
        product = self.product_1.copy(default={'default_code': False})
        self.assertEqual(
            product.default_code,
            False,
            "Product was not correctly duplicated!",
        )

    def test_05_product_duplicate(self):
        """Duplicate template when original doesn't have it."""
        self.product_1.product_tmpl_id.default_code = False
        product = self.product_1.product_tmpl_id.copy()
        self.assertEqual(
            product.default_code,
            False,
            "Product was not correctly duplicated!",
        )

    def test_06_product_duplicate(self):
        """Duplicate product when original doesn't have it."""
        self.product_1.default_code = False
        product = self.product_1.copy()
        self.assertEqual(
            product.default_code,
            False,
            "Product was not correctly duplicated!",
        )

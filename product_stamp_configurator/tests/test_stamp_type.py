from .common import TestProductStampConfiguratorCommon


class TestStampType(TestProductStampConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.ProductProduct.create(
            {'name': 'P1', 'categ_id': cls.product_categ_furniture.id}
        )
        cls.category_saleable = cls.product_categ_furniture.parent_id
        cls.category_all = cls.category_saleable.parent_id

    def test_01_product_stamp_type_from_category_direct(self):
        # WHEN
        self.category_saleable.stamp_type = 'die'
        # THEN
        self.assertEqual(self.product_1.stamp_type, 'counter_die')
        self.assertTrue(self.product_1.categ_id.validate_stamp_type('counter_die'))

    def test_02_product_stamp_type_from_category_parent(self):
        # GIVEN
        self.category_saleable.stamp_type = 'die'
        # WHEN
        self.product_categ_furniture.stamp_type = False
        # THEN
        self.assertEqual(self.product_1.stamp_type, 'die')
        self.assertTrue(self.product_1.categ_id.validate_stamp_type('die'))

    def test_03_product_stamp_type_from_category_parent_of_parent(self):
        # GIVEN
        (
            self.category_all | self.category_saleable | self.product_categ_furniture
        ).write({'stamp_type': False})
        self.assertEqual(self.product_1.stamp_type, False)
        # WHEN
        # Set this last to make sure, re-compute happens for multiple
        # category levels.
        self.category_all.stamp_type = 'mold'
        # THEN
        self.assertEqual(self.product_1.stamp_type, 'mold')
        self.assertTrue(self.product_1.categ_id.validate_stamp_type('mold'))

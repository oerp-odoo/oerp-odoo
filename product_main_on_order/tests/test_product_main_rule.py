from odoo.exceptions import ValidationError
from odoo.tests import common


class TestProductMainRule(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.ProductMainRule = cls.env['product.main.rule']
        (
            cls.product_in_rule_1,
            cls.product_in_rule_2,
            cls.product_in_rule_3,
            cls.product_not_in_rule_1,
            cls.product_not_in_rule_2,
            cls.product_not_in_rule_3,
        ) = cls.ProductProduct.create(
            [
                {'name': 'MY-PRODUCT-1'},
                {'name': 'MY-PRODUCT-2'},
                {'name': 'MY-PRODUCT-3'},
                {'name': 'MY-PRODUCT-4'},
                {'name': 'MY-PRODUCT-5'},
                {'name': 'MY-PRODUCT-6'},
            ]
        )
        (
            cls.product_main_rule_1,
            cls.product_main_rule_2,
            cls.product_main_rule_3,
            cls.product_main_rule_4,
        ) = cls.ProductMainRule.create(
            [
                {
                    'name': 'MY-RULE-1',
                    'product_id': cls.product_in_rule_1.id,
                    'sequence': 1,
                },
                {
                    'name': 'MY-RULE-2-FALLBACK',
                    'product_id': cls.product_in_rule_2.id,
                    'is_fallback': True,
                    'sequence': 5,
                },
                {
                    'name': 'MY-RULE-3',
                    'product_id': cls.product_in_rule_3.id,
                    'sequence': 10,
                },
                {
                    'name': 'MY-RULE-4',
                    'product_id': cls.product_in_rule_2.id,
                    'sequence': 15,
                },
            ]
        )

    def test_01_get_main_rule_matched(self):
        # WHEN
        res = self.ProductMainRule.get_main_rule(
            self.product_not_in_rule_1
            | self.product_in_rule_2
            | self.product_not_in_rule_3
        )
        # THEN
        self.assertEqual(res, self.product_main_rule_4)

    def test_02_get_main_rule_fallback(self):
        # WHEN
        res = self.ProductMainRule.get_main_rule(
            self.product_not_in_rule_1
            | self.product_not_in_rule_2
            | self.product_not_in_rule_3
        )
        # THEN
        self.assertEqual(res, self.product_main_rule_2)

    def test_03_get_main_rule_not_found(self):
        # GIVEN
        self.product_main_rule_2.is_fallback = False
        # WHEN
        res = self.ProductMainRule.get_main_rule(
            self.product_not_in_rule_1
            | self.product_not_in_rule_2
            | self.product_not_in_rule_3
        )
        # THEN
        # Fallback rule.
        self.assertEqual(res, self.ProductMainRule)

    def test_04_check_fallback_rule_unique(self):
        with self.assertRaises(ValidationError):
            self.product_main_rule_1.is_fallback = True

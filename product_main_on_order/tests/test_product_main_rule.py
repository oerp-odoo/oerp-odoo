from psycopg2 import IntegrityError

from odoo.tests import common
from odoo.tools import mute_logger


class TestProductMainRule(common.TransactionCase):
    """Test class for product main rule functionality."""

    @classmethod
    def setUpClass(cls):
        """Set demo data for product main rule tests."""
        super().setUpClass()
        cls.ProductMainRule = cls.env['product.main.rule']
        cls.product_main_rule_1 = cls.env.ref(
            'product_main_on_order.product_main_rule_1'
        )
        cls.product_main_rule_2 = cls.env.ref(
            'product_main_on_order.product_main_rule_2'
        )
        cls.product_main_rule_3 = cls.env.ref(
            'product_main_on_order.product_main_rule_3'
        )
        cls.product_main_rule_4 = cls.env.ref(
            'product_main_on_order.product_main_rule_4'
        )
        # Ones that are in rules.
        cls.product_5 = cls.env.ref('product.product_product_5')
        cls.product_6 = cls.env.ref('product.product_product_6')
        cls.product_7 = cls.env.ref('product.product_product_7')
        # Ones not in rules.
        cls.product_8 = cls.env.ref('product.product_product_8')
        cls.product_9 = cls.env.ref('product.product_product_9')
        cls.product_10 = cls.env.ref('product.product_product_10')

    def test_01_get_main_rule(self):
        """Find main rule when when product is matched."""
        res = self.ProductMainRule.get_main_rule(
            self.product_8 | self.product_6 | self.product_10
        )
        self.assertEqual(res, self.product_main_rule_4)

    def test_02_get_main_rule(self):
        """Find main rule when fallback is used."""
        res = self.ProductMainRule.get_main_rule(
            self.product_8 | self.product_9 | self.product_10
        )
        # Fallback rule.
        self.assertEqual(res, self.product_main_rule_2)

    def test_03_get_main_rule(self):
        """Try finding rule without any match and fallback rule."""
        self.product_main_rule_2.is_fallback = False
        res = self.ProductMainRule.get_main_rule(
            self.product_8 | self.product_9 | self.product_10
        )
        # Fallback rule.
        self.assertEqual(res, self.ProductMainRule)

    @mute_logger('odoo.sql_db')
    def test_04_check_fallback_rule_unique(self):
        """Check if only single fallback rule is allowed."""
        with self.assertRaises(IntegrityError):
            self.product_main_rule_1.is_fallback = True

from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tools import mute_logger
from odoo.tests.common import SavepointCase


class TestHsCodeCountry(SavepointCase):
    """Test class for HS Code functionality per country."""

    @classmethod
    def setUpClass(cls):
        """Set up data for HS Code tests."""
        super().setUpClass()
        # Models.
        cls.ProductProduct = cls.env['product.product']
        cls.ProductTemplateHsCode = cls.env['product.template.hs.code']
        # Templates/Products.
        # Desk.
        cls.product_template_desk = cls.env.ref(
            'product.product_product_4_product_template'
        )
        cls.product_template_desk.hs_code = '123456'
        cls.product_desk = cls.env.ref('product.product_product_4')
        # Chair.
        cls.product_chair = cls.env.ref('product.product_delivery_01')
        cls.product_template_chair = cls.product_chair.product_tmpl_id
        # Countries.
        cls.country_lt = cls.env.ref('base.lt')
        cls.country_us = cls.env.ref('base.us')
        cls.country_fr = cls.env.ref('base.fr')
        # HS Codes.
        hs_codes = cls.ProductTemplateHsCode.create([
            {
                'country_id': cls.country_lt.id,
                'product_tmpl_id': cls.product_template_desk.id,
            },
            {
                'code': '777',
                'country_id': cls.country_us.id,
                'is_origin_country': True,
                'product_tmpl_id': cls.product_template_desk.id,
            },
            {
                'code': '888',
                'country_id': cls.country_fr.id,
                'product_tmpl_id': cls.product_template_desk.id,
            },
        ])
        cls.hs_code_lt = hs_codes[0]
        cls.hs_code_us = hs_codes[1]
        cls.hs_code_fr = hs_codes[2]

    def test_01_retrieve_hs_code(self):
        """Retrieve HS code with country code specified (has HS codes).

        Case 1: 'lt' code passed.
        Case 2: 'us' code passed.
        Case 3: 'fr' code passed.
        Case 4: 'gb' code passed.

        """
        # Case 1.
        hs_code = self.product_desk.retrieve_hs_code('lt')
        self.assertEqual(self.product_desk.country_origin_id, self.country_us)
        self.assertEqual(hs_code, '123456')
        # Case 2.
        hs_code = self.product_desk.retrieve_hs_code('US')
        self.assertEqual(hs_code, '123456777')
        # Case 3.
        hs_code = self.product_desk.retrieve_hs_code('FR')
        # If can't find, will default to origin country HS code.
        self.assertEqual(hs_code, '123456888')
        # Case 4.
        hs_code = self.product_desk.retrieve_hs_code('Gb')
        # If can't find, will default to origin country HS code.
        self.assertEqual(hs_code, '123456777')

    def test_02_retrieve_hs_code(self):
        """Retrieve HS code with country code specified (no HS codes).

        Case 1: no main HS code.
        Case 2: has main HS code, 'us' code passed.
        Case 3: has main HS code, 'fr' code passed.

        """
        # Case 1.
        hs_code = self.product_chair.retrieve_hs_code('us')
        self.assertEqual(hs_code, False)
        # Case 2.
        self.product_chair.hs_code = '147852'
        hs_code = self.product_chair.retrieve_hs_code('fr')
        self.assertEqual(hs_code, '147852')
        # Case 3.
        hs_code = self.product_chair.retrieve_hs_code('fr')
        self.assertEqual(hs_code, '147852')

    def test_03_retrieve_hs_code(self):
        """Retrieve HS code with no code specified.

        Case 1: has country HS codes.
        Case 2: has only main HS code.
        """
        # Case 1.
        hs_code = self.product_desk.retrieve_hs_code(False)
        self.assertEqual(hs_code, '123456777')
        # Case 2.
        self.product_chair.hs_code = '987456'
        hs_code = self.product_chair.retrieve_hs_code(False)
        self.assertEqual(hs_code, '987456')

    def test_04_retrieve_hs_code(self):
        """Try to retrieve HS code on empty recordset and multi.

        Case 1: empty recordset.
        Case 2: multiple records in recordset.
        """
        # Case 1.
        self.assertEqual(self.ProductProduct.retrieve_hs_code('lt'), False)
        # Case 2.
        with self.assertRaises(ValueError):
            (self.product_desk | self.product_chair).retrieve_hs_code('lt')

    def test_05_check_hs_code(self):
        """Check if main HS code constraints with countries present.

        Case 1: try to make code less than 6 numbers.
        Case 2: try to make code more than 6 numbers.
        Case 3: try to use non digit symbols.
        Case 4: try to make code False.
        """
        # Case 1.
        with self.assertRaises(ValidationError):
            self.product_desk.hs_code = '123'
        with self.assertRaises(ValidationError):
            self.product_template_desk.hs_code = '321'
        # Case 2.
        with self.assertRaises(ValidationError):
            self.product_desk.hs_code = '1234567'
        # Case 3.
        with self.assertRaises(ValidationError):
            self.product_desk.hs_code = '12345X'
        # Case 4.
        with self.assertRaises(ValidationError):
            self.product_desk.hs_code = False

    def test_06_check_country_hs_code(self):
        """Check if HS code per country can be only digits."""
        with self.assertRaises(ValidationError):
            self.hs_code_lt.code = 'X123'

    def test_07_check_is_origin_country(self):
        """Make sure only one origin is allowed per product tmpl."""
        with self.assertRaises(ValidationError):
            self.hs_code_lt.is_origin_country = True
        with self.assertRaises(ValidationError):
            self.product_template_desk.hs_code_ids = [
                (
                    1,
                    self.hs_code_fr.id,
                    {'is_origin_country': True}
                )
            ]

    @mute_logger('odoo.sql_db')
    def test_08_check_hs_code_country_id(self):
        """Make sure country is unique per product template HS code."""
        with self.assertRaises(IntegrityError):
            self.hs_code_lt.country_id = self.country_us.id

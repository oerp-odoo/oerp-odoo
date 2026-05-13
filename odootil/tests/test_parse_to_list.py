from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..tools.parsing import parse_int_list, parse_positive_int_list, parse_to_list


class TestParseStringToList(TransactionCase):
    def test_01_parse_to_list_no_whitespace(self):
        self.assertEqual(parse_to_list('a,b'), ['a', 'b'])

    def test_02_parse_to_list_w_whitespace(self):
        self.assertEqual(parse_to_list('a, b'), ['a', ' b'])

    def test_03_parse_to_list_w_whitespace_cleaned(self):
        self.assertEqual(parse_to_list('a, b', clean_whitespace=True), ['a', 'b'])

    def test_04_parse_int_list_positive(self):
        self.assertEqual(parse_int_list('1,2'), [1, 2])
        self.assertEqual(parse_int_list('1, -2'), [1, -2])

    def test_05_parse_int_list_negative(self):
        self.assertEqual(parse_int_list('1, -2'), [1, -2])

    def test_06_parse_positive_int_list_positive(self):
        self.assertEqual(parse_positive_int_list('1, 2'), [1, 2])
        with self.assertRaisesRegex(ValidationError, r"Integers must be 0 or greater!"):
            self.assertEqual(parse_positive_int_list('1, -2'))

    def test_07_parse_positive_int_list_negative(self):
        with self.assertRaisesRegex(ValidationError, r"Integers must be 0 or greater!"):
            parse_positive_int_list('1, -2')

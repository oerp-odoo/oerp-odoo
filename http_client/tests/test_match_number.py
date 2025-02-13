from odoo.tests.common import TransactionCase

from ..utils import match_number


class TestMatchNumber(TransactionCase):
    def test_01_match_number_single_number_expr(self):
        # WHEN
        expr = '100'
        # THEN
        self.assertTrue(match_number(100, expr))
        self.assertFalse(match_number(200, expr))

    def test_02_match_number_not_single_number_expr(self):
        # WHEN
        expr = '!=100'
        # THEN
        self.assertFalse(match_number(100, expr))
        self.assertTrue(match_number(200, expr))

    def test_03_match_number_multi_number_expr(self):
        # WHEN
        expr = '100,200'
        # THEN
        self.assertTrue(match_number(100, expr))
        self.assertTrue(match_number(200, expr))
        self.assertFalse(match_number(300, expr))

    def test_04_match_number_multi_number_with_ne_expr(self):
        # WHEN
        expr = '100,!=200'
        # THEN
        self.assertTrue(match_number(100, expr))
        self.assertFalse(match_number(200, expr))
        # We explicitly match 100 and then everything else except 200!
        self.assertTrue(match_number(300, expr))

    def test_05_match_number_range_lt_expr(self):
        # WHEN
        expr = '<300'
        # THEN
        self.assertTrue(match_number(100, expr))
        self.assertTrue(match_number(200, expr))
        self.assertFalse(match_number(300, expr))

    def test_06_match_number_range_le_expr(self):
        # WHEN
        expr = '<=300'
        # THEN
        self.assertTrue(match_number(100, expr))
        self.assertTrue(match_number(200, expr))
        self.assertTrue(match_number(300, expr))
        self.assertFalse(match_number(301, expr))

    def test_07_match_number_range_le_expr(self):
        # WHEN
        expr = '<=300'
        # THEN
        self.assertTrue(match_number(100, expr))
        self.assertTrue(match_number(200, expr))
        self.assertTrue(match_number(300, expr))
        self.assertFalse(match_number(301, expr))

    def test_08_match_number_range_gt_expr(self):
        # WHEN
        expr = '>300'
        # THEN
        self.assertFalse(match_number(100, expr))
        self.assertFalse(match_number(200, expr))
        self.assertFalse(match_number(300, expr))
        self.assertTrue(match_number(301, expr))
        self.assertTrue(match_number(5000, expr))

    def test_09_match_number_range_ge_expr(self):
        # WHEN
        expr = '>=300'
        # THEN
        self.assertFalse(match_number(100, expr))
        self.assertFalse(match_number(200, expr))
        self.assertTrue(match_number(300, expr))
        self.assertTrue(match_number(301, expr))

    def test_10_match_number_range_gt_lt_expr(self):
        # WHEN
        expr = '>200,<400'
        # THEN
        self.assertFalse(match_number(100, expr))
        self.assertFalse(match_number(200, expr))
        self.assertTrue(match_number(300, expr))
        self.assertTrue(match_number(301, expr))

    def test_11_match_number_range_ge_lt_expr(self):
        # WHEN
        expr = '>=200,<400'
        # THEN
        self.assertFalse(match_number(100, expr))
        self.assertTrue(match_number(200, expr))
        self.assertTrue(match_number(300, expr))
        self.assertTrue(match_number(301, expr))

    def test_12_match_number_range_gt_le_expr(self):
        # WHEN
        expr = '>200, <=400'
        # THEN
        self.assertFalse(match_number(100, expr))
        self.assertFalse(match_number(200, expr))
        self.assertTrue(match_number(300, expr))
        self.assertTrue(match_number(301, expr))
        self.assertTrue(match_number(400, expr))
        self.assertFalse(match_number(401, expr))

    def test_13_match_number_range_ge_le_expr(self):
        # WHEN
        expr = '>=200,<=400 '
        # THEN
        self.assertFalse(match_number(100, expr))
        self.assertTrue(match_number(200, expr))
        self.assertTrue(match_number(300, expr))
        self.assertTrue(match_number(301, expr))
        self.assertTrue(match_number(400, expr))
        self.assertFalse(match_number(401, expr))

    def test_14_match_number_range_exact_ne_n_greater(self):
        # WHEN
        expr = '100,!=300,>=200'
        # THEN
        self.assertTrue(match_number(100, expr))
        self.assertTrue(match_number(200, expr))
        self.assertFalse(match_number(300, expr))
        self.assertTrue(match_number(301, expr))
        self.assertTrue(match_number(400, expr))
        self.assertTrue(match_number(401, expr))

    def test_15_match_number_multi_numbers_n_range_ge_le_expr(self):
        # WHEN
        expr = '50, 60,>=200,<=400'
        # THEN
        self.assertTrue(match_number(50, expr))
        self.assertTrue(match_number(60, expr))
        self.assertFalse(match_number(61, expr))
        self.assertFalse(match_number(100, expr))
        self.assertTrue(match_number(200, expr))
        self.assertTrue(match_number(300, expr))
        self.assertTrue(match_number(301, expr))
        self.assertTrue(match_number(400, expr))
        self.assertFalse(match_number(401, expr))

    def test_16_match_number_invalid_expr(self):
        msg = r"Invalid expression:"
        with self.assertRaisesRegex(ValueError, msg):
            match_number(50, '=400')
        with self.assertRaisesRegex(ValueError, msg):
            match_number(50, '!400')
        with self.assertRaisesRegex(ValueError, msg):
            match_number(50, '100.0')
        with self.assertRaisesRegex(ValueError, msg):
            match_number(50, '100,>=')
        with self.assertRaisesRegex(ValueError, msg):
            match_number(50, '100,')
        with self.assertRaisesRegex(ValueError, msg):
            match_number(50, ',100')

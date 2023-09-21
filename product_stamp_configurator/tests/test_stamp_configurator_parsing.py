from ..stamp.parsing import (
    is_insert_die_code,
    is_insert_die_in_code,
    parse_design_seq_code,
)
from .common import TestProductStampConfiguratorCommon


class TestStampConfiguratorParsing(TestProductStampConfiguratorCommon):
    def test_01_parse_design_seq_code_w_number_pfx(self):
        code = '1111F1B7 / 2222'
        # WHEN
        res = parse_design_seq_code(code, ('F', 'FE', 'E'))
        # THEN
        self.assertEqual(res, 'F1')

    def test_02_parse_design_seq_code_w_number_letter_pfx(self):
        # Two matches, but we only look for first match.
        code = 'A1111FEF1F2B7 / 2222'
        # WHEN
        res = parse_design_seq_code(code, ('F', 'FE', 'E'))
        # THEN
        self.assertEqual(res, 'F1')

    def test_03_parse_design_seq_code_missing_sequence(self):
        # Design code match, but it has no sequence after.
        code = 'A1111FEB7 / 2222'
        # WHEN
        res = parse_design_seq_code(code, ('F', 'FE', 'E'))
        # THEN
        self.assertEqual(res, '')

    def test_04_parse_design_seq_code_missing_design_code(self):
        code = 'A1111XYB7 / 2222'
        # WHEN
        res = parse_design_seq_code(code, ('F', 'FE', 'E'))
        # THEN
        self.assertEqual(res, '')

    def test_05_is_insert_die_code_yes(self):
        self.assertTrue(is_insert_die_code('i'))

    def test_06_is_insert_die_code_capital(self):
        self.assertFalse(is_insert_die_code('I'))

    def test_07_is_insert_die_code_not_exact_match(self):
        self.assertFalse(is_insert_die_code('ii'))

    def test_08_insert_die_code_next_to_f(self):
        # No design codes to compare to.
        self.assertTrue(
            is_insert_die_in_code(
                '230634iF1B4 / 1245454', design_codes=('F', 'FE', 'E')
            )
        )

    def test_09_insert_die_code_next_to_fe(self):
        self.assertTrue(
            is_insert_die_in_code(
                '230634iFE1B4 / 1245454', design_codes=('F', 'FE', 'E')
            )
        )

    def test_10_insert_die_in_code_no_i(self):
        self.assertFalse(
            is_insert_die_in_code(
                '230634FE1B4 / 1245454', design_codes=('F', 'FE', 'E')
            )
        )

    def test_11_insert_die_in_code_i_is_capital(self):
        self.assertFalse(
            is_insert_die_in_code(
                '230634IFE1B4 / 1245454', design_codes=('F', 'FE', 'E')
            )
        )

    def test_12_insert_die_in_code_design_codes_not_match(self):
        self.assertFalse(
            is_insert_die_in_code(
                '230634iCD1B4 / 1245454', design_codes=('F', 'FE', 'E')
            )
        )

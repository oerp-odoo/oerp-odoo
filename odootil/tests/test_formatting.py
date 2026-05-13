from ..tools.formatting import unaccent
from .common import TestOdootilCommon


class TestFormatting(TestOdootilCommon):
    def test_01_unaccent_non_ascii(self):
        self.assertEqual(unaccent('abcčdėę'), 'abccdee')

    def test_02_unaccent_ascii(self):
        self.assertEqual(unaccent('abccdee'), 'abccdee')

from odoo.tests.common import TransactionCase

from ..tools.collections import Prefix, PrefixSet


class TestStrPrefixIn(TransactionCase):
    def test_01_prefix_in(self):
        self.assertTrue(Prefix('A') in ['A1', 'B1'])

    def test_02_prefix_not_in(self):
        self.assertFalse(Prefix('C') in ['A1', 'B1'])

    def test_03_prefix_tuple_in(self):
        self.assertTrue((Prefix('A'), Prefix('B')) in [('A1', 'B1')])

    def test_04_prefix_tuple_not_in(self):
        self.assertFalse((Prefix('A'), Prefix('B')) in [('B1', 'A1')])

    def test_05_prefix_set_in(self):
        self.assertTrue(PrefixSet([Prefix('A'), Prefix('B')]) in [{'B1', 'A1'}])

    def test_06_prefix_set_mix_in(self):
        self.assertTrue(PrefixSet([Prefix('A'), 'B1']) in [{'B1', 'A1'}])

    def test_07_prefix_set_not_in(self):
        self.assertFalse(PrefixSet([Prefix('A'), Prefix('B')]) in [{'B1', 'C1'}])

    def test_08_prefix_set_mix_not_in(self):
        self.assertFalse(PrefixSet([Prefix('A'), 'B2']) in [{'B1', 'A1'}])

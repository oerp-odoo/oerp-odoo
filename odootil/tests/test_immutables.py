from odoo.tests.common import TransactionCase

from ..tools.immutables import deep_freeze_dict

SECRET_1 = b"secret123"
DATA_1 = b"data123"


class TestImmutables(TransactionCase):
    def test_01_deep_freeze_dict(self):
        # GIVEN
        dct = {'a': 10, 'b': {'c': 20, 'd': {'e': 30}}}
        # WHEN
        res = deep_freeze_dict(dct)
        # THEN
        with self.assertRaises(NotImplementedError):
            res['a'] = 'x'
        with self.assertRaises(NotImplementedError):
            res['b'] = 'x'
        with self.assertRaises(NotImplementedError):
            res['b']['c'] = 'x'
        with self.assertRaises(NotImplementedError):
            res['b']['d'] = 'x'
        with self.assertRaises(NotImplementedError):
            res['b']['d']['e'] = 'x'
        with self.assertRaises(NotImplementedError):
            res['z'] = 'x'

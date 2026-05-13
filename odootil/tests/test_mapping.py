from odoo.tests.common import TransactionCase

from ..tools.mapping import get_nested, pop_nested


class TestMapping(TransactionCase):
    def test_01_get_nested_first_level(self):
        # WHEN
        res = get_nested({'a': {'b': 10}}, ['a'])
        # THEN
        self.assertEqual(res, {'b': 10})

    def test_02_get_nested_second_level(self):
        # WHEN
        res = get_nested({'a': {'b': 10}}, ['a', 'b'])
        # THEN
        self.assertEqual(res, 10)

    def test_03_get_nested_not_matched(self):
        # WHEN
        res = get_nested({'a': {'b': 10}}, ['a', 'b', 'c'])
        # THEN
        self.assertEqual(res, None)

    def test_04_pop_nested_first_level(self):
        # GIVEN
        data = {'a': {'b': 10}}
        # WHEN
        res = pop_nested(data, ['a'])
        # THEN
        self.assertEqual(res, {'b': 10})
        self.assertEqual(data, {})

    def test_05_pop_nested_second_level(self):
        # GIVEN
        data = {'a': {'b': 10}}
        # WHEN
        res = pop_nested(data, ['a', 'b'])
        # THEN
        self.assertEqual(res, 10)
        self.assertEqual(data, {'a': {}})

    def test_06_pop_nested_not_matched(self):
        # GIVEN
        data = {'a': {'b': 10}}
        # WHEN
        res = pop_nested(data, ['a', 'b', 'c'])
        # THEN
        self.assertEqual(res, None)
        self.assertEqual(data, {'a': {'b': 10}})

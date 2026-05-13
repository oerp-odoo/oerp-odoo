from . import common


class TestOrderbyHelpers(common.TestOdootilCommon):
    """Class to test orderby helper methods."""

    def test_01_to_writable_keys(self):
        """Check if 'id' is removed from keys."""
        keys = self.ResPartner.to_writable_keys(['a', 'b', 'id'])
        self.assertEqual(keys, ['a', 'b'])
        keys = self.ResPartner.to_writable_keys(['b', 'c'])
        self.assertEqual(keys, ['b', 'c'])

    def test_02_orderby_to_keys(self):
        """_order with keys without options."""
        res = self.ResPartner.orderby_to_keys('name, sequence, id')
        self.assertEqual(res, ['name', 'sequence', 'id'])

    def test_03_orderby_to_keys(self):
        """_order with desc, asc options."""
        res = self.ResPartner.orderby_to_keys('name asc,sequence desc, id')
        self.assertEqual(res, ['name', 'sequence', 'id'])

    def test_04_orderby_to_keys(self):
        """_order with mixed options."""
        res = self.ResPartner.orderby_to_keys(
            'name NULLS FIRST, sequence desc NULLS LAST, id asc nulls last'
        )
        self.assertEqual(res, ['name', 'sequence', 'id'])

    def test_05_orderby_to_keys(self):
        """_order with asc desc as keys."""
        res = self.ResPartner.orderby_to_keys('asc desc, desc')
        self.assertEqual(res, ['asc', 'desc'])

    def test_06_orderby_to_keys(self):
        """_order with one key only."""
        res = self.ResPartner.orderby_to_keys('id')
        self.assertEqual(res, ['id'])

    def test_07_orderby_to_writable_keys(self):
        """_order with mixed options -> writable keys."""
        res = self.ResPartner.orderby_to_writable_keys(
            'name NULLS FIRST, sequence desc NULLS LAST, id asc nulls last'
        )
        self.assertEqual(res, ['name', 'sequence'])

    def test_08_orderby_to_sort_keys(self):
        """Sort keys _order without options."""
        res = self.ResPartner.orderby_to_sort_keys('name, sequence, id')
        self.assertEqual(res, [('name', False), ('sequence', False), ('id', False)])

    def test_09_orderby_to_sort_keys(self):
        """Sort keys _order with desc, asc options."""
        res = self.ResPartner.orderby_to_sort_keys('name asc,sequence desc, id')
        self.assertEqual(res, [('name', False), ('sequence', True), ('id', False)])

    def test_10_orderby_to_sort_keys(self):
        """Sort keys _order with mixed options."""
        res = self.ResPartner.orderby_to_sort_keys(
            'name NULLS FIRST, sequence desc NULLS LAST, id asc nulls last'
        )
        self.assertEqual(res, [('name', False), ('sequence', True), ('id', False)])

    def test_11_orderby_to_sort_keys(self):
        """Sort keys _order with asc desc as keys."""
        res = self.ResPartner.orderby_to_sort_keys('asc desc, desc')
        self.assertEqual(res, [('asc', True), ('desc', False)])

    def test_12_orderby_to_sort_keys(self):
        """Sort keys _order with one key only."""
        res = self.ResPartner.orderby_to_sort_keys('id')
        self.assertEqual(res, [('id', False)])

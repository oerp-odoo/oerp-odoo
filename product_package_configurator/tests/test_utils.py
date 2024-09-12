from odoo.tests.common import TransactionCase

from .. import utils


class TestUtils(TransactionCase):
    def test_01_calc_lamination_area(self):
        # WHEN
        res = utils.lamination.calc_area(20000, 10500)
        # THEN
        # (base_wrapping_area + lid_wrapping_area) * 1.2 / 1000000
        # (20000 + 10500) * 1.2 / 1000000
        self.assertEqual(res, 0.0366)

    def test_02_calc_area_price(self):
        # WHEN
        res = utils.misc.calc_area_price(2, 0.0366)
        # THEN
        self.assertEqual(res, 0.0732)

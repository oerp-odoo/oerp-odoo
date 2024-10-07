from odoo.tests.common import TransactionCase

from .. import utils
from ..value_objects.layout import Layout2D, LayoutFitter


class TestUtils(TransactionCase):
    def test_01_calc_lamination_area(self):
        # WHEN
        res = utils.lamination.calc_area(20000, 10500)
        # THEN
        # (base_wrapping_area + lid_wrapping_area) * 1.2 / 1000000
        # (20000 + 10500) * 1.2 / 1000000
        self.assertEqual(res, 0.0366)

    def test_02_multiply_no_digits_limit(self):
        # WHEN
        res = utils.misc.multiply(2, 0.8888)
        # THEN
        self.assertEqual(res, 1.7776)

    def test_03_multiply_two_digits(self):
        # WHEN
        res = utils.misc.multiply(2, 0.8888, digits=2)
        # THEN
        self.assertEqual(res, 1.78)

    def test_04_update_by_target_two_numbers_up(self):
        self.assertEqual(utils.misc.update_by_target(50, 17, 20), (23, 27))

    def test_05_update_by_target_two_numbers_down(self):
        self.assertEqual(utils.misc.update_by_target(10, 17, 20), (5, 5))

    def test_06_update_by_target_two_numbers_down_equal_numbers(self):
        self.assertEqual(utils.misc.update_by_target(30, 20, 20), (15, 15))

    def test_07_update_by_target_two_numbers_up_equal_numbers(self):
        self.assertEqual(utils.misc.update_by_target(50, 20, 20), (25, 25))

    def test_08_fitter_calc_fit_quantity_single(self):
        # GIVEN
        fitter = LayoutFitter(
            product_layout=Layout2D(length=999, width=699),
            sheet_layout=Layout2D(length=1000, width=700),
        )
        # WHEN
        qty = utils.fitter.calc_fit_quantity(fitter)
        # THEN
        self.assertEqual(qty, 1)

    def test_09_fitter_calc_fit_quantity_three(self):
        # GIVEN
        fitter = LayoutFitter(
            product_layout=Layout2D(length=550, width=300),
            sheet_layout=Layout2D(length=1000, width=700),
        )
        # WHEN
        qty = utils.fitter.calc_fit_quantity(fitter)
        # THEN
        self.assertEqual(qty, 3)

    def test_10_fitter_calc_fit_quantity_length_not_fit(self):
        # GIVEN
        fitter = LayoutFitter(
            product_layout=Layout2D(length=1001, width=400),
            sheet_layout=Layout2D(length=1000, width=700),
        )
        # WHEN
        qty = utils.fitter.calc_fit_quantity(fitter)
        # THEN
        self.assertEqual(qty, 0)

    def test_11_fitter_calc_fit_quantity_width_not_fit(self):
        # GIVEN
        fitter = LayoutFitter(
            product_layout=Layout2D(length=999, width=701),
            sheet_layout=Layout2D(length=1000, width=700),
        )
        # WHEN
        qty = utils.fitter.calc_fit_quantity(fitter)
        # THEN
        self.assertEqual(qty, 0)

    def test_12_fitter_calc_sheet_quantity_min_qty(self):
        self.assertEqual(utils.fitter.calc_sheet_quantity(100, 3), 34)

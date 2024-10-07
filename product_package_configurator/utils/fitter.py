"""Functions to calculate how many same size products fit on a specific size sheet.

This is similar to 2D bin packing problem, but it is a simpler one, because products to
fit are always of the same size.
"""
import math

from ..value_objects.layout import LayoutFitter


def calc_fit_quantity(fitter: LayoutFitter):
    """Calculate how many product layouts fit on single sheet."""

    def calc_side_fit(product_layout, carton_length, carton_width):
        return math.floor(carton_length / product_layout.length) * math.floor(
            carton_width / product_layout.width
        )

    product_layout = fitter.product_layout
    sheet_layout = fitter.sheet_layout
    # We try to fit product layout two ways and see with which one it can fit more.
    qty_one = calc_side_fit(product_layout, sheet_layout.length, sheet_layout.width)
    qty_two = calc_side_fit(product_layout, sheet_layout.width, sheet_layout.length)
    return max([qty_one, qty_two])


def calc_fit_quantity_multi(fitters: list[LayoutFitter]):
    quantities = []
    for fitter in fitters:
        quantities.append(calc_fit_quantity(fitter))
    return quantities


def calc_sheet_quantity(product_qty: int, fit_qty: int):
    """Calculate how many sheets are needed.

    Args:
        product_qty: how much products need to be produced.
        fit_qty: number of products that fit on single sheet.

    """
    return math.ceil(product_qty / fit_qty)

from odoo import models

from ..utils.fitter import calc_sheet_quantity
from ..utils.misc import update_by_target
from ..value_objects.sheet import SheetQuantity


class PackageSheetQuantity(models.AbstractModel):
    _name = 'package.sheet.quantity'
    _description = "Package Sheet Quantity"

    def calc(self, quantity: int, sheet_quantities: list[SheetQuantity]):
        """Calculate needed sheets quantity by fit quantity.

        If different parts have same sheet material, calculations are
        grouped to make sure minimum order quantity is not duplicated!
        """
        res = {}
        for sheet in sheet_quantities:
            res.update(self._calc(quantity, sheet))
        return res

    def _calc(self, quantity: int, sheet_quantity: SheetQuantity):
        quantities = []
        for item in sheet_quantity.items:
            quantities.append(
                calc_sheet_quantity(quantity, item.fit_qty) + item.setup_raw_qty
            )
        total_qty = sum(quantities)
        if sheet_quantity.min_qty > total_qty:
            quantities = update_by_target(sheet_quantity.min_qty, *quantities)
        res = {}
        for qty, item in zip(quantities, sheet_quantity.items):
            res[item.code] = qty
        return res

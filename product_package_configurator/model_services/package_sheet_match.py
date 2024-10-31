from odoo import models

from ..utils.fitter import calc_fit_quantity
from ..value_objects.layout import Layout2D, LayoutFitter


class PackageSheetMatch(models.Model):
    """Service to find most cost effective sheet."""

    _name = 'package.sheet.match'
    _description = "Package Sheet Match"

    def match(self, sheet_type, product_layout: Layout2D):
        """Find sheet using its type where it is the most cost effective."""
        sheet_model = self.env[self._get_sheet_type_map()[sheet_type.scope]]
        sheets = sheet_model.search(self._prepare_sheet_domain(sheet_type))
        return self._match(sheets, product_layout)

    def _match(self, sheets, product_layout: Layout2D):
        # TODO: should we take into account min_qty of a sheet? Though then
        # we would need to know what quantity would need to be produced as there could
        # be multiple circulations..
        matches = []
        if not sheets:
            return sheets
        for sheet in sheets:
            fit_qty = calc_fit_quantity(
                LayoutFitter(
                    product_layout=product_layout,
                    sheet_layout=Layout2D(
                        length=sheet.sheet_length, width=sheet.sheet_width
                    ),
                )
            )
            # We compare it by how much single fit_qty would cost on single raw sheet!
            matches.append((sheet, sheet.unit_cost / fit_qty))
        return min(matches, key=lambda x: x[1])[0]

    def _prepare_sheet_domain(self, sheet_type):
        return [('sheet_type_id', '=', sheet_type.id)]

    def _get_sheet_type_map(self):
        return {
            'greyboard': 'package.sheet.greyboard',
            'wrappingpaper': 'package.sheet.wrappingpaper',
        }

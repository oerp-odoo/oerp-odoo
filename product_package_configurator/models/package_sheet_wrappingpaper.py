from odoo import fields, models

from ..const import SheetTypeScope


class PackageSheetWrappingpaper(models.Model):

    _name = 'package.sheet.wrappingpaper'
    _inherit = 'package.sheet'
    _description = "Package Sheet Wrapping Paper"

    sheet_type_id = fields.Many2one(
        domain=[('scope', '=', SheetTypeScope.WRAPPINGPAPER)],
    )

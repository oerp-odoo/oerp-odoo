from odoo import fields, models

from ..const import SheetTypeScope


class PackageWrappingpaper(models.Model):

    _name = 'package.wrappingpaper'
    _inherit = 'package.sheet'
    _description = "Package Wrapping Paper"

    sheet_type_id = fields.Many2one(
        domain=[('scope', '=', SheetTypeScope.WRAPPINGPAPER)],
    )

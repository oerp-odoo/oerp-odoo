from odoo import fields, models

from ..const import SheetTypeScope


class PackageSheetGreyboard(models.Model):

    _name = 'package.sheet.greyboard'
    _inherit = 'package.sheet'
    _description = "Package Sheet Grey Board"

    sheet_type_id = fields.Many2one(domain=[('scope', '=', SheetTypeScope.GREYBOARD)])

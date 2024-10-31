from odoo import fields, models

from ..const import SheetTypeScope


class PackageCarton(models.Model):

    _name = 'package.carton'
    _inherit = 'package.sheet'
    _description = "Package Carton"

    sheet_type_id = fields.Many2one(domain=[('scope', '=', SheetTypeScope.GREYBOARD)])

from odoo import api, fields, models


class PackageWrappingpaper(models.Model):

    _name = 'package.wrappingpaper'
    _inherit = 'package.sheet'
    _description = "Package Wrapping Paper"

    # TODO: should wrapping paper have thickness field like carton?
    name = fields.Char(required=True)

    @api.depends('name', 'sheet_length', 'sheet_width')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'{rec.name} {rec.sheet_length:g}x{rec.sheet_width:g}mm'

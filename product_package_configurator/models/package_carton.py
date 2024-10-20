from odoo import api, fields, models


class PackageCarton(models.Model):

    _name = 'package.carton'
    _inherit = 'package.sheet'
    _description = "Package Carton"

    name = fields.Char(required=True)
    thickness = fields.Float("Thickness, mm", required=True)

    @api.depends('name', 'thickness', 'sheet_length', 'sheet_width')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f'{rec.name} '
                + f'{rec.thickness:2g}x{rec.sheet_length:2g}x{rec.sheet_width:2g}mm'
            )

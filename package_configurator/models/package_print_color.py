from odoo import fields, models


class PackagePrintColor(models.Model):
    _name = 'package.print.color'
    _description = "Package Print Color"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

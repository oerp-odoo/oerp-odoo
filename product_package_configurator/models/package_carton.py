from odoo import fields, models


class PackageCarton(models.Model):

    _name = 'package.carton'
    _description = "Package Carton"

    name = fields.Char(required=True)
    thickness = fields.Float("Thickness, mm", required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

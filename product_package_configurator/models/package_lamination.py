from odoo import fields, models


class PackageLamination(models.Model):

    _name = 'package.lamination'
    _description = "Package Lamination"

    name = fields.Char(required=True)
    price_unit = fields.Float(required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
